# views.py - Library AI Agent (schema-corrected for library_* tables)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import re
import requests
import os
from typing import Dict, List, Optional
from django.db import connections
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count

# If you still import Django models elsewhere, keep them; unused imports removed
# from .models import Author, Book, Course, User
# from .enhanced_models import Category, EnhancedAuthor, EnhancedBook, Article, WebApp, Company
# from .enhanced_agent import EnhancedAIAgent
# from .link_generator import ArabicLinkGenerator, QueryResponseBuilder

# ====== GROQ CONFIG (read from env; do NOT hardcode secrets) ======
GROQ_API_KEY = os.getenv("your groq api ")
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = os.getenv("GROQ_MODEL", "compound-beta")
GROQ_TEMPERATURE = float(os.getenv("GROQ_TEMPERATURE", "0.0"))
GROQ_MAX_TOKENS = int(os.getenv("GROQ_MAX_TOKENS", "1024"))
GROQ_TIMEOUT = int(os.getenv("GROQ_TIMEOUT", "25"))

# ====== EXACT TABLE MAPPING ======
TABLES = {
    "books": "library_books",
    "authors": "library_authors",
    "categories": "library_categories",
}

# Junction table candidates (we'll autodetect which exists)
JUNCTION_TABLE_CANDIDATES = [
    # Common Django m2m names (depending on app label / model names / db_table overrides)
    "library_books_categories",
    "library_book_categories",
    "library_books_category",
    "library_book_category",
    "library_librarybookcategory",
    "LibraryBookCategory",  # quoted usage would keep case, but we'll detect existence
]

# ====== COMPREHENSIVE DATABASE SCHEMA (YOUR REAL COLUMNS) ======
DATABASE_SCHEMA = {
    "library_books": {
        "columns": [
            "id", "user_id", "title", "description", "author_id", "file",
            "bookCover", "status", "stop_rating", "view_count", "featured",
            "total_ratings", "average_rating", "pdf_page_count", "bookmark_count",
            "download_count", "short_url", "shortio_link_id", "slug",
            "buy_link", "amazon_buy_link", "created_at", "updated_at"
        ],
        "search_columns": ["title", "description", "slug", "buy_link", "amazon_buy_link", "short_url"],
        "joins": {
            "author": "JOIN library_authors a ON b.author_id = a.id",
            # categories join will use runtime-resolved junction table name
            "categories": "JOIN __BOOK_CATEGORY_JUNCTION__ bc ON b.id = bc.book_id "
                          "JOIN library_categories c ON bc.category_id = c.id",
        },
        "alias": "b",
    },
    "library_authors": {
        "columns": [
            "id", "name", "bio", "profile_pic", "slug",
            "wikipedia", "youtube", "X_twitter", "famous_personalities",
            "short_url", "shortio_link_id", "created_at", "updated_at"
        ],
        "search_columns": ["name", "bio", "slug", "wikipedia", "youtube", "X_twitter", "short_url"],
        "alias": "a",
    },
    "library_categories": {
        "columns": [
            "id", "name", "icon", "status", "favicon_icon", "color",
            "wikipedia", "description", "short_url", "shortio_link_id",
            "slug", "created_at", "updated_at"
        ],
        "search_columns": ["name", "description", "slug", "wikipedia", "short_url"],
        "alias": "c",
    }
}

# ====== LANGUAGE DETECTION ======
def detect_language(text: str) -> str:
    if not text:
        return "english"
    arabic_chars = sum(1 for ch in text if '\u0600' <= ch <= '\u06FF')
    total_chars = sum(1 for ch in text if ch.isalpha())
    if total_chars == 0:
        return "english"
    return "arabic" if (arabic_chars / total_chars) > 0.3 else "english"

# ====== SIMPLE SLUG + LINK GENERATION (msarii.com) ======
import unicodedata
def create_slug(text):
    if not text:
        return ""
    text = str(text).strip().lower()
    # strip diacritics
    text = ''.join(
        c for c in unicodedata.normalize('NFKD', text)
        if not unicodedata.combining(c)
    )
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text

def generate_msarii_link(item_type, name_or_title, slug=None):
    base_urls = {
        'author': 'https://msarii.com/authors/',
        'book': 'https://msarii.com/book-detail/',
        'category': 'https://msarii.com/categories/',
    }
    final_slug = slug or create_slug(name_or_title)
    return f"{base_urls.get(item_type, 'https://msarii.com/')}{final_slug}"

# ====== HELPERS: ensure we SELECT-only, detect junction table, and swap placeholder ======
def _ensure_select_only(sql: str) -> bool:
    sql_stripped = sql.strip().lower()
    # Allow WITH ... SELECT too
    return bool(re.match(r'^(with\s+.+?select|select)\b', sql_stripped, flags=re.DOTALL))

def _detect_junction_table(cursor) -> Optional[str]:
    """
    Try to find which junction table exists by probing candidates with a harmless EXISTS check.
    """
    for name in JUNCTION_TABLE_CANDIDATES:
        try:
            # Use information_schema if available; fallback to SELECT 1
            cursor.execute(f"SELECT 1 FROM {name} LIMIT 1")
            # If it didn't throw, we found it
            return name
        except Exception:
            continue
    return None

def _apply_junction_placeholder(sql_query: str, cursor) -> str:
    if "__BOOK_CATEGORY_JUNCTION__" not in sql_query:
        return sql_query
    jt = _detect_junction_table(cursor)
    if not jt:
        # If not found, keep a dummy that will fail clearly with message
        return sql_query.replace("__BOOK_CATEGORY_JUNCTION__", "/*UNKNOWN_JUNCTION_TABLE*/")
    return sql_query.replace("__BOOK_CATEGORY_JUNCTION__", jt)

# ====== ENHANCED GROQ API CALL ======
def call_groq_chat(question: str) -> str:
    lang = detect_language(question)
    answer_lang = "Arabic" if lang == "arabic" else "English"


    schema_text = """
DATABASE SCHEMA (tables and important columns):

1) library_books (alias b)
    id, user_id, title, description, author, file, bookCover, status, stop_rating,
    view_count, featured, total_ratings, average_rating, pdf_page_count, bookmark_count,
    download_count, short_url, shortio_link_id, slug, buy_link, amazon_buy_link, created_at, updated_at

2) library_authors (alias a)
    id, name, bio, profile_pic, slug, wikipedia, youtube, X_twitter, famous_personalities,
    short_url, shortio_link_id, created_at, updated_at

3) library_categories (alias c)
    id, name, icon, status, favicon_icon, color, wikipedia, description, short_url,
    shortio_link_id, slug, created_at, updated_at

MANY-TO-MANY:
- Books ↔ Categories via junction table LibraryBookCategory (alias j)
  Columns: librarybook_id, category_id

RELATIONSHIPS:
- b.author = a.id
- b.id = j.librarybook_id AND c.id = j.category_id
"""

    system_prompt = f"""You are a precise SQL generator for a library database.

CRITICAL RULES:
1. Return ONLY ONE SQL query in a code block: ```sql\nSELECT ...\n```
2. Use ONLY the exact table/column names above. Never use any table or column not listed.
3. For text search, use LOWER(column) LIKE LOWER('%term%').
4. For counts, return COUNT(*) AS cnt.
5. For book-author queries, JOIN library_books b with library_authors a (b.author = a.id).
6. For book-category queries, JOIN using LibraryBookCategory j (b.id = j.librarybook_id, c.id = j.category_id).
7. Add LIMIT 10 for lists unless counting.
8. Answer in {answer_lang}.
9. Never modify data; SELECT only.
10. Use aliases: b=books, a=authors, c=categories, j=LibraryBookCategory.

COMMON PATTERNS:
- "how many books" → SELECT COUNT(*) AS cnt FROM library_books
- "books by author X" → SELECT COUNT(*) AS cnt FROM library_books b JOIN library_authors a ON b.author = a.id WHERE LOWER(a.name) LIKE LOWER('%author_name%')
- "books with no author" → SELECT COUNT(*) AS cnt FROM library_books WHERE author IS NULL
- "authors with no book" → SELECT COUNT(*) AS cnt FROM library_authors a WHERE a.id NOT IN (SELECT b.author FROM library_books b)
- "is book X available" → SELECT COUNT(*) FROM library_books WHERE LOWER(title) LIKE LOWER('%book_title%')
- "who wrote book X" → SELECT a.name FROM library_books b JOIN library_authors a ON b.author = a.id WHERE LOWER(b.title) LIKE LOWER('%book_title%')
- "books in category X" → SELECT b.title FROM library_books b JOIN LibraryBookCategory j ON b.id = j.librarybook_id JOIN library_categories c ON j.category_id = c.id WHERE LOWER(c.name) = 'category_name'
- "author info" → SELECT * FROM library_authors WHERE LOWER(name) LIKE LOWER('%author_name%')
"""

    user_prompt = f"User question: {question}"

    if not GROQ_API_KEY:
        raise RuntimeError("Missing GROQ_API_KEY environment variable")

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": GROQ_MODEL,
        "temperature": GROQ_TEMPERATURE,
        "max_tokens": GROQ_MAX_TOKENS,
        "messages": [
            {"role": "system", "content": system_prompt + "\n" + schema_text},
            {"role": "user", "content": user_prompt},
        ],
    }

    response = requests.post(GROQ_BASE_URL, headers=headers, json=payload, timeout=GROQ_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

# ====== SQL EXTRACTION ======
def extract_sql_from_response(content: str):
    if not content:
        return None
    patterns = [
        r'```sql\s*(.*?)\s*```',
        r'```\s*(SELECT.*?)(?:\s*```|$)',
        r'(SELECT\s+.*?)(?:;|$)',
    ]
    for pattern in patterns:
        m = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if m:
            sql = m.group(1).strip()
            sql = re.sub(r'\s+', ' ', sql).rstrip(';').strip()
            return sql
    return None

# ====== SQL EXECUTION ======
def execute_sql_directly(sql_query: str):
    if not sql_query:
        return {"success": False, "error": "No SQL query provided"}

    if not _ensure_select_only(sql_query):
        return {"success": False, "error": "Only SELECT queries are allowed", "sql_query": sql_query}

    try:
        with connections['default'].cursor() as cursor:
            # Replace junction placeholder if present
            sql_to_run = _apply_junction_placeholder(sql_query, cursor)

            cursor.execute(sql_to_run)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            results = []
            for row in rows:
                row_dict = dict(zip(columns, row))

                # Add msarii links based on fields present
                if 'title' in row_dict or 'slug' in row_dict:
                    # Book?
                    if "library_books" in sql_to_run or 'title' in row_dict:
                        title = row_dict.get('title', '')
                        row_dict['msarii_link'] = generate_msarii_link('book', title, row_dict.get('slug'))
                if 'name' in row_dict:
                    # Author or Category; decide heuristically via columns in query
                    if "library_authors" in sql_to_run:
                        row_dict['msarii_link'] = generate_msarii_link('author', row_dict['name'], row_dict.get('slug'))
                    elif "library_categories" in sql_to_run:
                        row_dict['msarii_link'] = generate_msarii_link('category', row_dict['name'], row_dict.get('slug'))

                results.append(row_dict)

            return {
                "success": True,
                "results": results,
                "count": len(results),
                "sql_query": sql_to_run
            }
    except Exception as e:
        return {"success": False, "error": str(e), "sql_query": sql_query}

# ====== SMART FALLBACKS FOR COMMON QUERIES (fast path) ======

# ====== RESPONSE FORMATTING ======
def format_response_for_user(sql_result, query_language="english"):
    """
    Format the raw SQL result into a user-friendly response.
    Uses existing specialized formatting first, then applies AI polishing
    for natural human-like phrasing.
    """

    # Handle errors
    if not sql_result.get("success"):
        error_msg = sql_result.get("error", "Unknown error")
        return (
            f"❌ خطأ في الاستعلام: {error_msg}"
            if query_language == "arabic"
            else f"❌ Query error: {error_msg}"
        )

    results = sql_result.get("results", [])
    count = sql_result.get("count", 0)

    # No results found
    if count == 0:
        return (
            "📭 لم يتم العثور على نتائج"
            if query_language == "arabic"
            else "📭 No results found"
        )

    sql = sql_result.get("sql_query", "")
    base_response = None

    # Count-only
    if len(results) == 1 and "cnt" in results[0]:
        cnt = results[0]["cnt"]
        base_response = (
            f"📊 العدد: {cnt}"
            if query_language == "arabic"
            else f"📊 Count: {cnt}"
        )

    # Specialized formatting (books, authors, categories, etc.)
    elif "library_books" in sql:
        base_response = format_book_results(results, query_language)
    elif "library_authors" in sql:
        base_response = format_author_results(results, query_language)
    elif "library_categories" in sql:
        base_response = format_category_results(results, query_language)
    else:
        base_response = format_generic_results(results, query_language)

    # --- AI polishing step ---
    try:
        rows_preview = str(results[:5])  # only send first few rows
        language_prompt = "Arabic" if query_language == "arabic" else "English"

        prompt = f"""
You are an assistant that reformats SQL query results into clear,
user-friendly {language_prompt} sentences.

SQL Query: {sql}
Results (first rows): {rows_preview}
Row count: {len(results)}

Base response (system-generated): {base_response}

Task:
- Rewrite the base response into a natural, polite {language_prompt} sentence.
- If it's a list, summarize and mention some examples.
- If it's a count, phrase it as a sentence ("There are X ...").
- If base response is missing or unclear, rely on results + SQL.
"""

        ai_response = call_groq_chat(prompt)  # 🔹 replace with your Groq call
        return JsonResponse({"response": ai_response.strip()})

    except Exception:
        # fallback: return base response if AI fails
        return base_response


def format_book_results(results, language="english"):
    is_arabic = (language == "arabic")
    parts = [f"📚 تم العثور على {len(results)} كتاب:" if is_arabic else f"📚 Found {len(results)} book(s):"]
    for i, book in enumerate(results, 1):
        title = book.get('title') or ('بدون عنوان' if is_arabic else 'Untitled')
        name = book.get('author_name') or book.get('name')  # if joined author columns included
        info = f"\n{i}. 📖 {title}"
        if name:
            info += f"\n   ✍️ المؤلف: {name}" if is_arabic else f"\n   ✍️ Author: {name}"
        if book.get('description'):
            # Remove HTML tags for user-friendly output
            desc_raw = book['description']
            desc_clean = re.sub(r'<[^>]+>', '', desc_raw)
            desc = desc_clean[:120] + ("..." if len(desc_clean) > 120 else "")
            info += f"\n   📝 {desc}"
        if 'msarii_link' in book:
            info += f"\n   🔗 رابط الكتاب: {book['msarii_link']}" if is_arabic else f"\n   🔗 Book Link: {book['msarii_link']}"
        elif book.get('slug'):
            info += f"\n   🔗 {generate_msarii_link('book', title, book['slug'])}"
        if book.get('status'):
            info += f"\n   🏷️ الحالة: {book['status']}" if is_arabic else f"\n   🏷️ Status: {book['status']}"
        if book.get('view_count') is not None:
            info += f"\n   👁️‍🗨️ المشاهدات: {book['view_count']}" if is_arabic else f"\n   👁️‍🗨️ Views: {book['view_count']}"
        parts.append(info)
    return "\n".join(parts)

def format_author_results(results, language="english"):
    is_arabic = (language == "arabic")
    parts = [f"✍️ تم العثور على {len(results)} مؤلف:" if is_arabic else f"✍️ Found {len(results)} author(s):"]
    for i, a in enumerate(results, 1):
        name = a.get('name') or ('بدون اسم' if is_arabic else 'Unnamed')
        bio = a.get('bio') or ""
        info = f"\n{i}. 👤 {name}"
        if bio:
            info += f"\n   📝 {bio[:150]}{'...' if len(bio) > 150 else ''}"
        if a.get('wikipedia'):
            info += f"\n   📖 ويكيبيديا: {a['wikipedia']}" if is_arabic else f"\n   📖 Wikipedia: {a['wikipedia']}"
        if a.get('youtube'):
            info += f"\n   📺 يوتيوب: {a['youtube']}" if is_arabic else f"\n   📺 YouTube: {a['youtube']}"
        if a.get('X_twitter'):
            info += f"\n   🐦 تويتر/X: {a['X_twitter']}" if is_arabic else f"\n   🐦 Twitter/X: {a['X_twitter']}"
        if 'msarii_link' in a:
            info += f"\n   🔗 الملف الشخصي: {a['msarii_link']}" if is_arabic else f"\n   🔗 Profile: {a['msarii_link']}"
        elif a.get('slug'):
            info += f"\n   🔗 {generate_msarii_link('author', name, a['slug'])}"
        parts.append(info)
    return "\n".join(parts)

def format_category_results(results, language="english"):
    is_arabic = (language == "arabic")
    parts = [f"📂 تم العثور على {len(results)} فئة:" if is_arabic else f"📂 Found {len(results)} category/categories:"]
    for i, c in enumerate(results, 1):
        name = c.get('name') or ('بدون اسم' if is_arabic else 'Unnamed')
        info = f"\n{i}. 📁 {name}"
        if c.get('description'):
            info += f"\n   📝 {c['description'][:120]}{'...' if len(c['description']) > 120 else ''}"
        if 'msarii_link' in c:
            info += f"\n   🔗 رابط الفئة: {c['msarii_link']}" if is_arabic else f"\n   🔗 Category Link: {c['msarii_link']}"
        elif c.get('slug'):
            info += f"\n   🔗 {generate_msarii_link('category', name, c['slug'])}"
        parts.append(info)
    return "\n".join(parts)

def format_generic_results(results, language="english"):
    is_arabic = (language == "arabic")
    parts = [f"📋 تم العثور على {len(results)} نتيجة:" if is_arabic else f"📋 Found {len(results)} result(s):"]
    for i, r in enumerate(results, 1):
        line = f"\n{i}. "
        for k, v in r.items():
            if k != 'msarii_link' and v is not None and v != "":
                line += f"{k}: {v}, "
        if 'msarii_link' in r:
            line += f"\n   🔗 {r['msarii_link']}"
        parts.append(line.rstrip(", "))
    return "\n".join(parts)

# ====== MAIN API VIEWS ======
@method_decorator(csrf_exempt, name='dispatch')
class AIQueryView(APIView):
    """Main AI Query endpoint with Groq integration (schema-corrected)"""

    def post(self, request):
        try:
            # Get question (supports JSON / form)
            question = None
            if hasattr(request, 'data') and request.data:
                question = request.data.get("question")
            if not question and hasattr(request, 'POST'):
                question = request.POST.get("question")
            if not question and hasattr(request, 'body') and request.body:
                try:
                    question = json.loads(request.body.decode('utf-8')).get("question")
                except Exception:
                    pass

            if not question:
                return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)

            language = detect_language(question)

            # Always go via Groq → SQL
            try:
                groq_response = call_groq_chat(question)
                sql_query = extract_sql_from_response(groq_response)

                if not sql_query:
                    return Response({
                        "response": "لم أتمكن من فهم السؤال" if language == "arabic" else "Could not understand the question",
                        "success": False,
                        "raw_response": groq_response
                    }, status=status.HTTP_200_OK)

                sql_result = execute_sql_directly(sql_query)
                formatted_response = format_response_for_user(sql_result, language)

                return Response({
                    "response": formatted_response,
                    "success": sql_result.get("success", False),
                    "executed_sql": sql_result.get("sql_query", sql_query),
                    "result_count": sql_result.get("count", 0),
                    "language": language,
                    "method": "groq"
                }, status=status.HTTP_200_OK)

            except Exception as groq_error:
                error_msg = f"❌ خطأ في النظام: {str(groq_error)}" if language == "arabic" else f"❌ System error: {str(groq_error)}"
                return Response({"response": error_msg, "success": False}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "response": f"❌ خطأ عام: {str(e)}" if detect_language(question or "") == "arabic" else f"❌ General error: {str(e)}",
                "success": False
            }, status=status.HTTP_200_OK)

@csrf_exempt
@require_http_methods(["POST"])
def simple_ai_query(request):
    try:
        question = request.POST.get('question')
        if not question and request.body:
            try:
                question = json.loads(request.body.decode('utf-8')).get('question')
            except Exception:
                pass

        if not question:
            return JsonResponse({"error": "Question is required", "success": False}, status=400)

        language = detect_language(question)

        # Always go via Groq → SQL
        groq_response = call_groq_chat(question)
        sql_query = extract_sql_from_response(groq_response)

        if not sql_query:
            return JsonResponse({
                "response": "لم أتمكن من فهم السؤال" if language == "arabic" else "Could not understand the question",
                "success": False
            })

        sql_result = execute_sql_directly(sql_query)
        formatted_response = format_response_for_user(sql_result, language)

        return JsonResponse({
            "response": formatted_response,
            "success": sql_result.get("success", False),
            "executed_sql": sql_result.get("sql_query", sql_query).replace('\n', ' '),
            "result_count": sql_result.get("count", 0),
            "language": language,
            "method": "groq"
        })

    except Exception as e:
        return JsonResponse({"response": f"❌ {str(e)}", "success": False}, status=500)

# ====== DATABASE TEST VIEW (updated to your tables) ======
class TestDatabaseView(APIView):
    """Test DB connectivity and show sample data"""

    def get(self, request):
        try:
            results = {}
            with connections['default'].cursor() as cursor:
                for key, table_name in TABLES.items():
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                        rows = cursor.fetchall()
                        columns = [desc[0] for desc in cursor.description]
                        sample_data = [dict(zip(columns, row)) for row in rows]
                        results[key] = {
                            "table_name": table_name,
                            "total_records": count,
                            "sample_data": sample_data,
                            "columns": columns
                        }
                    except Exception as e:
                        results[key] = {"table_name": table_name, "error": str(e)}

                # detect and report the junction table we will use
                jt = _detect_junction_table(cursor)

            return Response({
                "database_status": "connected",
                "tables": results,
                "total_tables": len(TABLES),
                "junction_table_detected": jt,
                "schema_info": DATABASE_SCHEMA
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"database_status": "error", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ====== BASIC STATS VIEW (using your tables) ======
class LibraryStatsView(APIView):
    """Get library statistics"""

    def get(self, request):
        try:
            stats = {}
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM library_books")
                stats['total_books'] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM library_authors")
                stats['total_authors'] = cursor.fetchone()[0]

                cursor.execute("SELECT COUNT(*) FROM library_categories")
                stats['total_categories'] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT COUNT(a.id)
                    FROM library_authors a
                    LEFT JOIN library_books b ON a.id = b.author_id
                    WHERE b.id IS NULL
                """)
                stats['authors_without_books'] = cursor.fetchone()[0]

                cursor.execute("""
                    SELECT a.name, COUNT(b.id) AS book_count
                    FROM library_authors a
                    LEFT JOIN library_books b ON a.id = b.author_id
                    GROUP BY a.id, a.name
                    ORDER BY book_count DESC
                    LIMIT 10
                """)
                top_authors = cursor.fetchall()
                stats['top_authors'] = [{"name": row[0], "book_count": row[1]} for row in top_authors]

            return Response({"success": True, "statistics": stats}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
