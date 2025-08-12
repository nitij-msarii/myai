from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
from typing import Annotated, Dict, List
from django.db import connections
from .models import Author, Book, Course, User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os
import re
import urllib.parse
import html

# Make AutoGen optional; always have a safe dummy agent available
class _DummyAgent:
    def __init__(self, *args, **kwargs):
        pass

    def register_for_llm(self, *args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

    def register_for_execution(self, *args, **kwargs):
        def decorator(fn):
            return fn
        return decorator

    def initiate_chat(self, *args, **kwargs):
        raise RuntimeError("AutoGen is not available in this environment")

try:
    from autogen import ConversableAgent, UserProxyAgent
    AUTOGEN_AVAILABLE = True
except Exception:
    AUTOGEN_AVAILABLE = False

# Initialize Conversable Agents with better Groq model
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
os.environ["AUTOGEN_USE_DOCKER"] = "False"

# Using a better Groq model for improved performance
llm_config = {
    "cache_seed": 48,
    "config_list": [{
        "model": "llama-3.1-70b-versatile",  # Better model for complex queries
        "api_key": GROQ_API_KEY,
        "api_type": "groq",
        "base_url": "https://api.groq.com/openai/v1",
        "temperature": 0.1,  # Lower temperature for more consistent responses
        "max_tokens": 2048
    }],
}

# Enhanced SQL Writer Agent with Arabic and English support
if AUTOGEN_AVAILABLE and GROQ_API_KEY:
    sql_writer = ConversableAgent(
        "sql_writer",
        llm_config=llm_config,
        system_message="""You are an expert multilingual database assistant specializing in Arabic and English queries. Your tasks:

1. LANGUAGE DETECTION: Detect if the user query is in Arabic or English
2. QUERY ANALYSIS: Understand what the user is asking for (books, authors, courses, etc.)
3. DATABASE SEARCH: Generate appropriate SQL queries for the Django models
4. RESPONSE FORMATTING: Respond in the same language as the query

DATABASE SCHEMA:
- AI_agent_author: id, name (Arabic), bio (Arabic), link, created_at
- AI_agent_book: id, title (Arabic), author_id, isbn, description (Arabic), link, genre (Arabic), publication_date, pages, language, created_at
- AI_agent_course: id, title (Arabic), description (Arabic), instructor (Arabic), link, duration (Arabic), level (Arabic), created_at
- AI_agent_user: id, username, email, full_name (Arabic), created_at

LINK GENERATION RULES:
- Authors: https://msarii.com/authors/{arabic_name_slug}
- Books: https://msarii.com/books/{arabic_title_slug}
- Courses: https://msarii.com/courses/{arabic_title_slug}
- Articles: https://msarii.com/articles/{arabic_title_slug}
- Categories: https://msarii.com/categories/{arabic_category_slug}

Always use execute_sql_api() function with proper reflection and SQL query."""
    )

    user_proxy = UserProxyAgent(
        "user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=2,
        code_execution_config=False
    )
else:
    # Fallback placeholders to avoid initialization errors when API key is missing
    sql_writer = _DummyAgent()
    user_proxy = _DummyAgent()

# Helper functions for Arabic language support and link generation
def detect_language(text):
    """Detect if text is primarily Arabic or English"""
    arabic_chars = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    total_chars = len([char for char in text if char.isalpha()])
    if total_chars == 0:
        return "english"
    arabic_ratio = arabic_chars / total_chars
    return "arabic" if arabic_ratio > 0.3 else "english"

def create_slug(text):
    """Create URL-friendly slug from Arabic or English text"""
    if not text:
        return ""
    # For Arabic text, we'll use the text as-is but URL encode it
    # For English text, we'll create a standard slug
    text = str(text).strip()
    if detect_language(text) == "arabic":
        return urllib.parse.quote(text, safe='')
    else:
        # Standard English slug creation
        text = re.sub(r'[^\w\s-]', '', text.lower())
        return re.sub(r'[-\s]+', '-', text).strip('-')

def generate_msarii_link(item_type, name_or_title):
    """Generate msarii.com links based on item type and name/title"""
    base_url = "https://msarii.com"
    slug = create_slug(name_or_title)

    link_mapping = {
        'author': f"{base_url}/authors/{slug}",
        'book': f"{base_url}/books/{slug}",
        'course': f"{base_url}/courses/{slug}",
        'article': f"{base_url}/articles/{slug}",
        'category': f"{base_url}/categories/{slug}",
        'company': f"{base_url}/companies/{slug}",
        'webapp': f"{base_url}/webapps/{slug}"
    }

    return link_mapping.get(item_type, f"{base_url}/{slug}")

def translate_response(text, target_language):
    """Simple response translation helper"""
    if target_language == "arabic":
        # Basic translations for common terms
        translations = {
            "Found": "تم العثور على",
            "Book": "كتاب",
            "Author": "مؤلف",
            "Course": "دورة",
            "Title": "العنوان",
            "Description": "الوصف",
            "Link": "الرابط",
            "No results found": "لم يتم العثور على نتائج",
            "Error": "خطأ",
            "Available": "متوفر",
            "Not available": "غير متوفر"
        }
        for en, ar in translations.items():
            text = text.replace(en, ar)
    return text

# Enhanced SQL Execution with Arabic support and link generation
def execute_sql(reflection: str, sql: str):
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(sql)
            results = cursor.fetchall()

            # Get column names for better formatting
            column_names = [desc[0] for desc in cursor.description]

            # Format results as list of dictionaries with enhanced data
            formatted_results = []
            for row in results:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[column_names[i]] = value

                # Add generated links based on the data type and available fields
                if 'name' in row_dict and any(table in sql.lower() for table in ['library_authors', 'author']):
                    # Author link using name or slug
                    link_text = row_dict.get('slug', row_dict['name'])
                    row_dict['msarii_link'] = generate_msarii_link('author', link_text)

                elif 'title' in row_dict and any(table in sql.lower() for table in ['library_encyclopedia_book', 'library_books', 'book']):
                    # Book link using title or slug
                    link_text = row_dict.get('slug', row_dict['title'])
                    row_dict['msarii_link'] = generate_msarii_link('book', link_text)

                elif 'title' in row_dict and any(table in sql.lower() for table in ['library_articles', 'article']):
                    # Article link using title or slug
                    link_text = row_dict.get('slug', row_dict['title'])
                    row_dict['msarii_link'] = generate_msarii_link('article', link_text)

                elif 'name' in row_dict and any(table in sql.lower() for table in ['library_company', 'company']):
                    link_text = row_dict.get('slug', row_dict['name'])
                    row_dict['msarii_link'] = generate_msarii_link('company', link_text)

                elif 'name' in row_dict and any(table in sql.lower() for table in ['library_webapps', 'webapp']):
                    link_text = row_dict.get('slug', row_dict['name'])
                    row_dict['msarii_link'] = generate_msarii_link('webapp', link_text)

                # Add author link if author info is present
                if 'author_name' in row_dict and row_dict['author_name']:
                    author_slug = row_dict.get('author_slug', row_dict['author_name'])
                    row_dict['author_msarii_link'] = generate_msarii_link('author', author_slug)

                formatted_results.append(row_dict)

            return {
                "success": True,
                "results": formatted_results,
                "count": len(formatted_results),
                "sql_query": sql,
                "reflection": reflection
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sql_query": sql,
            "reflection": reflection
        }

@sql_writer.register_for_llm(description="Execute a SQL query and return detailed results with all available information.")
@user_proxy.register_for_execution()
def execute_sql_api(
    reflection: Annotated[str, "Detailed reasoning about what SQL query to generate"], 
    sql: Annotated[str, "Complete SQL query to execute"]
) -> Annotated[Dict[str, any], "Dictionary with results, count, and metadata"]:
    return execute_sql(reflection, sql)

def get_relevant_schema():
    schema = {}

    with connections['default'].cursor() as cursor:
        try:
            # Get all tables depending on DB vendor
            vendor = connections['default'].vendor
            if vendor == 'sqlite':
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                existing_tables = [row[0] for row in cursor.fetchall()]
            else:
                cursor.execute("SHOW TABLES;")
                existing_tables = [row[0] for row in cursor.fetchall()]

            print(f"[DEBUG] Found tables: {existing_tables}")

            # Use ALL tables discovered in the database for the agent schema
            relevant_tables = existing_tables
            print(f"[DEBUG] Using all tables: {relevant_tables}")

            for table in relevant_tables:
                try:
                    # Get table structure depending on DB vendor
                    vendor = connections['default'].vendor
                    if vendor == 'sqlite':
                        cursor.execute(f"PRAGMA table_info({table});")
                        columns = cursor.fetchall()
                        # SQLite columns: cid, name, type, notnull, dflt_value, pk
                        schema[table] = [{
                            "name": col[1],
                            "type": col[2],
                            "null": 'NO' if col[3] else 'YES',
                            "key": 'PRI' if col[5] else ''
                        } for col in columns]
                    else:
                        cursor.execute(f"DESCRIBE {table};")
                        columns = cursor.fetchall()
                        # MySQL: Field, Type, Null, Key, Default, Extra
                        schema[table] = [{"name": col[0], "type": col[1], "null": col[2], "key": col[3]} for col in columns]
                except Exception as e:
                    print(f"Error getting schema for {table}: {e}")
                    schema[table] = []
        except Exception as e:
            print(f"Error getting table list: {e}")
            schema = {}

    return schema

def generate_enhanced_prompt(schema, question):
    if not schema:
        language = detect_language(question)
        if language == "arabic":
            return f"""قاعدة البيانات فارغة. سؤال المستخدم: {question}. أخبر المستخدم أن قاعدة البيانات فارغة."""
        else:
            return f"""Database appears empty. User Question: {question}. Inform user database is empty."""

    # Detect query language
    query_language = detect_language(question)

    return f"""You are an expert multilingual database assistant. Your task is to read the user's question and generate ONE correct SQL query that answers it using ONLY the tables and columns listed in the schema below.

USER QUESTION ({query_language}): {question}

DATABASE SCHEMA (ALL TABLES AND COLUMNS):
{json.dumps(schema, indent=2, ensure_ascii=False)}

STRICT INSTRUCTIONS:
- Use ONLY tables and columns that appear in the schema above. Never invent columns.
- Choose the most relevant table(s) based on the question (books, authors, articles, companies, webapps, categories, etc.).
- Prefer JOINs when you need related information (e.g., book with author details).
- If the question is about counts (how many/كم/عدد), generate a SELECT COUNT(*) query.
- Limit result size appropriately (e.g., LIMIT 5) unless the question requests all.
- Return the SQL using the execute_sql_api function with a brief reflection of your reasoning.
- Respond in the same language as the question when describing your reasoning.
"""

def extract_sql_from_response(content):
    """Extract SQL query from the agent's response"""
    # Look for SQL queries in the response
    sql_patterns = [
        r'```sql\s*(.*?)\s*```',
        r'```\s*(SELECT.*?)\s*```',
        r'execute_sql\([^)]*,\s*["\'](.*?)["\']',
        r'SQL:\s*(SELECT.*?)(?:\n|$)',
        r'Query:\s*(SELECT.*?)(?:\n|$)',
        r'"sql":\s*"(SELECT.*?)"',
        r'"sql":\s*"(SELECT.*?)"',
        r'sql.*?:\s*"(SELECT.*?)"',
        r'<function=execute_sql_api>.*?"sql":\s*"(SELECT.*?)"',
        r'function=execute_sql_api.*?"sql":\s*"(SELECT.*?)"'
    ]
    
    for pattern in sql_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        if matches:
            sql = matches[0].strip()
            # Clean up the SQL if it has escaped quotes
            sql = sql.replace('\\"', '"').replace('\\n', ' ')
            return sql
    
    # If no SQL found, try to extract any SELECT statement
    select_pattern = r'SELECT.*?(?:;|$)'
    matches = re.findall(select_pattern, content, re.IGNORECASE | re.DOTALL)
    if matches:
        sql = matches[0].strip()
        sql = sql.replace('\\"', '"').replace('\\n', ' ')
        return sql
    
    return None

def execute_sql_directly(sql_query):
    """Execute SQL query directly and return results"""
    if not sql_query:
        return {"success": False, "error": "No SQL query found"}
    
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(sql_query)
            results = cursor.fetchall()
            
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            
            # Format results
            formatted_results = []
            for row in results:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[column_names[i]] = value
                formatted_results.append(row_dict)
            
            return {
                "success": True,
                "results": formatted_results,
                "count": len(formatted_results),
                "sql_query": sql_query
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "sql_query": sql_query
        }

# Deterministic COUNT intent utilities

def clean_search_text(text: str) -> str:
    t = (text or '')
    # Remove Arabic question marks and punctuation
    t = re.sub(r"[؟?\u061F\u060C,.;!]+", " ", t)
    # Remove common phrases (Arabic/English) and generic tokens like 'كتاب'
    removal = [
        "من هو", "من هي", "who is", "what is", "هل لديك", "هل", "كتاب",
        # English generic list phrasing
        "any", "from db", "book name", "book names", "show", "list", "give me", "fetch"
    ]
    for phrase in removal:
        t = re.sub(rf"\b{re.escape(phrase)}\b", " ", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_limit_from_question(text: str, default: int = 5) -> int:
    try:
        m = re.search(r"(\d+)", text or "")
        if m:
            n = int(m.group(1))
            if n < 1:
                return default
            return min(n, 50)
    except Exception:
        pass
    return default

def detect_count_intent(question: str) -> bool:
    q = (question or '')
    ql = q.lower()
    return ('how many' in ql or 'count' in ql or 'كم' in q or 'عدد' in q or 'كم عدد' in q)


def infer_entity_type_from_patterns(question: str):
    q = (question or '')
    if re.search(r"^\s*من\s+(هو|هي)\s+", q):
        return 'author'
    return None


def pick_table_by_keywords(schema: dict, keywords: List[str]):
    if not schema:
        return None
    for table in schema.keys():
        name = table.lower()
        if any(kw in name for kw in keywords):
            return table
    return None


def find_columns(schema: dict, table: str, substrings: List[str]):
    cols = []
    for col in schema.get(table, []):
        cname = col.get('name') or ''
        if any(s in cname.lower() for s in substrings):
            cols.append(cname)
    return cols


def build_dynamic_author_sql(schema: dict, question: str):
    # Choose author-like table
    table = pick_table_by_keywords(schema, ['author'])
    if not table:
        return None
    # Determine name-like columns
    name_cols = find_columns(schema, table, ['name', 'slug']) or ['name']
    qtext = clean_search_text(question)
    if not qtext:
        return None
    # Build WHERE with OR across name-like columns
    conditions = [f"{table}.{c} LIKE '%{qtext}%'" for c in name_cols]
    where = " OR ".join(conditions)
    sql = f"SELECT {table}.* FROM {table} WHERE {where} LIMIT 5"
    return sql


def has_column(schema: dict, table: str, col: str) -> bool:
    for c in schema.get(table, []):
        if (c.get('name') or '').lower() == col.lower():
            return True
    return False


def pick_author_table(schema: dict):
    return pick_table_by_keywords(schema, ['author'])


def pick_primary_book_table(schema: dict):
    preferred = ['library_books', 'library_encyclopedia_book', 'library_books_encyclopedia']
    for p in preferred:
        if p in schema:
            return p
    # Choose any 'book' table excluding auxiliary fragments
    exclude_fragments = ['bookmark', 'history', 'review', 'reviews', 'category', 'addition', 'webapp', 'website', 'schedule']
    for table in schema.keys():
        name = table.lower()
        if ('book' in name or 'books' in name) and not any(ex in name for ex in exclude_fragments):
            return table
    return None


def build_dynamic_book_sql(schema: dict, question: str):
    table = pick_primary_book_table(schema)
    if not table:
        return None
    title_cols = find_columns(schema, table, ['title_ar', 'title', 'name']) or ['title']
    qtext = clean_search_text(question)

    # Extract requested limit (defaults to 5)
    limit_n = extract_limit_from_question(question, 5)

    # If query looks like a generic list request (no specific title tokens), return LIMIT only
    generic_list = (not qtext) or (len(qtext) < 3)
    list_markers = ["any", "show", "list", "give me", "fetch"]
    if any(marker in (question or '').lower() for marker in list_markers):
        generic_list = True

    # Try to join author if available
    a_table = pick_author_table(schema)
    a_name_cols = find_columns(schema, a_table, ['name']) if a_table else []
    join_clause = ""
    author_select = ""
    if has_column(schema, table, 'author_id') and a_table and a_name_cols:
        a_name = a_name_cols[0]
        join_clause = f" LEFT JOIN {a_table} ON {table}.author_id = {a_table}.id"
        author_select = f", {a_table}.{a_name} as author_name"

    if generic_list:
        return f"SELECT {table}.*{author_select} FROM {table}{join_clause} LIMIT {limit_n}"

    # Otherwise, build WHERE with OR across title-like columns
    conditions = [f"{table}.{c} LIKE '%{qtext}%'" for c in title_cols]
    where = " OR ".join(conditions)
    return f"SELECT {table}.*{author_select} FROM {table}{join_clause} WHERE {where} LIMIT {limit_n}"


def infer_entity_type(question: str):
    q = (question or '')
    mapping = {
        'book': ['كتاب', 'كتب', 'book', 'books'],
        'author': ['مؤلف', 'كاتب', 'عالم', 'author', 'authors'],
        'article': ['مقال', 'مقالات', 'article', 'articles'],
        'category': ['فئة', 'تصنيف', 'نوع', 'category', 'categories'],
        'company': ['شركة', 'شركات', 'company', 'companies'],
        'webapp': ['تطبيق', 'تطبيقات', 'برنامج', 'برامج', 'webapp', 'webapps'],
    }
    for t, kws in mapping.items():
        for kw in kws:
            if kw in q:
                return t
    return None


def get_tables_for_type(schema: dict, entity_type: str):
    if not schema or not entity_type:
        return []
    keyword_map = {
        'book': ['book', 'books', 'encyclopedia'],
        'author': ['author', 'authors'],
        'article': ['article', 'articles'],
        'category': ['category', 'categories'],
        'company': ['company'],
        'webapp': ['webapp', 'webapps'],
    }
    keywords = keyword_map.get(entity_type, [])
    tables = []
    for table in schema.keys():
        name = table.lower()
        if any(kw in name for kw in keywords):
            tables.append(table)
    return tables


def count_rows_in_tables(tables: list):
    results = []
    with connections['default'].cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                count = cursor.fetchone()[0]
                results.append({'table': table, 'count': count})
            except Exception as e:
                results.append({'table': table, 'error': str(e)})
    return results


def format_count_response(counts: list, language: str = 'english', entity_type: str = None):
    if not counts:
        return "📭 No matching tables found." if language != 'arabic' else "📭 لم يتم العثور على جداول مطابقة."

    # Helper to pick primary tables per entity for human-friendly reporting
    def pick_primary(items, etype):
        tbls = [i for i in items if 'count' in i]
        if etype == 'book':
            preferred = [
                'library_books',
                'library_encyclopedia_book',
                'library_books_encyclopedia'
            ]
            # Filter out auxiliary tables (bookmarks/reviews/history/category additions etc.)
            exclude_fragments = ['bookmark', 'history', 'review', 'reviews', 'category', 'addition', 'webapp', 'website', 'schedule']
            primary = [i for i in tbls if (i['table'] in preferred)]
            if not primary:
                primary = [i for i in tbls if ('book' in i['table'].lower() or 'books' in i['table'].lower()) and not any(ex in i['table'].lower() for ex in exclude_fragments)]
            return primary
        elif etype == 'author':
            preferred = ['library_authors']
            return [i for i in tbls if i['table'] in preferred] or tbls[:3]
        elif etype == 'article':
            candidates = [i for i in tbls if 'article' in i['table'].lower()]
            return candidates or tbls[:3]
        elif etype == 'company':
            candidates = [i for i in tbls if 'company' in i['table'].lower()]
            return candidates or tbls[:3]
        elif etype == 'webapp':
            candidates = [i for i in tbls if 'webapp' in i['table'].lower()]
            return candidates or tbls[:3]
        elif etype == 'category':
            candidates = [i for i in tbls if 'categor' in i['table'].lower()]
            return candidates or tbls[:3]
        return tbls[:5]

    display = pick_primary(counts, entity_type)
    total = sum(int(i['count']) for i in display if 'count' in i)

    if language == 'arabic':
        et = (entity_type or '').strip()
        parts = []
        if et == 'book':
            parts.append(f"📚 لدينا حاليًا ما يقرب من {total} كتاب/كتب في قاعدة البيانات.")
            parts.append("تفصيل الجداول الأساسية:")
        else:
            header_map = {
                'author': 'المؤلفين',
                'article': 'المقالات',
                'company': 'الشركات',
                'webapp': 'تطبيقات الويب',
                'category': 'التصنيفات'
            }
            label = header_map.get(et, 'السجلات')
            parts.append(f"📊 إجمالي {label} التقريبي: {total}")
            parts.append("تفصيل الجداول الأساسية:")
        for item in display:
            parts.append(f" - {item['table']}: {item['count']}")
        # Note about hidden auxiliary tables
        if len(display) < len([i for i in counts if 'count' in i]):
            parts.append("ℹ️ تم إخفاء الجداول المساعدة (المراجعات/المفضلات/السجل) للوضوح.")
        return "\n".join(parts)
    else:
        et = (entity_type or '').strip()
        parts = []
        if et == 'book':
            parts.append(f"📚 We currently have approximately {total} book(s) in the database.")
            parts.append("Key source tables:")
        else:
            header_map = {
                'author': 'author(s)',
                'article': 'article(s)',
                'company': 'company(ies)',
                'webapp': 'web app(s)',
                'category': 'category(ies)'
            }
            label = header_map.get(et, 'record(s)')
            parts.append(f"📊 Approximate total {label}: {total}")
            parts.append("Key source tables:")
        for item in display:
            parts.append(f" - {item['table']}: {item['count']}")
        if len(display) < len([i for i in counts if 'count' in i]):
            parts.append("ℹ️ Auxiliary tables (reviews/bookmarks/history) are hidden for clarity.")
        return "\n".join(parts)

# Text sanitization helpers

def sanitize_text(val) -> str:
    if val is None:
        return ""
    try:
        s = html.unescape(str(val))
        s = re.sub(r'<[^>]+>', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s
    except Exception:
        try:
            return str(val)
        except Exception:
            return ""

# SQL explanation helpers

def extract_tables_from_sql(sql: str) -> List[str]:
    if not sql:
        return []
    try:
        pattern = re.compile(r"\bFROM\s+([\w\.]*)|\bJOIN\s+([\w\.]*)", re.IGNORECASE)
        tables = []
        for m in pattern.finditer(sql):
            t = m.group(1) or m.group(2)
            if t and t not in tables:
                tables.append(t)
        return tables
    except Exception:
        return []


def build_explanation_note(sql: str, language: str) -> str:
    tables = extract_tables_from_sql(sql)
    if language == 'arabic':
        if tables:
            joined = ", ".join(tables)
            return f"شرح: تم توليد SQL اعتمادًا على المخطط الحي لقاعدة البيانات واختيار الجداول الأنسب ({joined}). تم عرض الروابط للتنقل السريع."
        else:
            return "شرح: تم توليد SQL اعتمادًا على المخطط الحي لقاعدة البيانات. تم تضمين روابط مناسبة ضمن النتائج."
    else:
        if tables:
            joined = ", ".join(tables)
            return f"Explanation: The SQL was generated using the live DB schema and selected the most relevant tables ({joined}). Related links are included for quick navigation."
        else:
            return "Explanation: The SQL was generated using the live DB schema. Appropriate links are included in the results."


def format_response_for_user(sql_result, query_language="english"):
    """Format SQL results into a user-friendly response with Arabic support"""
    if not sql_result.get("success"):
        error_msg = sql_result.get("error", "Unknown error")
        if "no such table" in error_msg.lower():
            if query_language == "arabic":
                return "❌ لم يتم العثور على جداول مطابقة في قاعدة البيانات. قاعدة البيانات فارغة أو لا تحتوي على نوع البيانات المطلوب.\n\n💡 جرب السؤال عن البيانات المتاحة، أو أضف بعض البيانات إلى قاعدة البيانات أولاً."
            else:
                return "❌ No matching tables found in the database. The database appears to be empty or doesn't contain the requested data type.\n\n💡 Try asking about what data is available, or add some data to the database first."

        if query_language == "arabic":
            return f"❌ خطأ في تنفيذ الاستعلام: {error_msg}"
        else:
            return f"❌ Error executing query: {error_msg}"

    results = sql_result.get("results", [])
    count = sql_result.get("count", 0)

    if count == 0:
        if query_language == "arabic":
            return "📭 لم يتم العثور على نتائج لاستعلامك. قاعدة البيانات قد تكون فارغة أو البيانات المطلوبة غير موجودة."
        else:
            return "📭 No results found for your query. The database might be empty or the requested data doesn't exist."

    # Format based on the type of data
    if any("title" in result and "author" in str(result) for result in results):
        return format_book_results(results, query_language)
    elif any("name" in result and "bio" in str(result) for result in results):
        return format_author_results(results, query_language)
    elif any("instructor" in str(result) for result in results):
        return format_course_results(results, query_language)
    else:
        return format_general_results(results, query_language)

def format_book_results(results, language="english"):
    """Format book-related results with comprehensive field support and Arabic language"""
    if language == "arabic":
        response = f"تم العثور على {len(results)} كتاب/كتب:\n\n"

        for i, book in enumerate(results, 1):
            response += f"📚 **الكتاب {i}:**\n"

            # Basic book info
            if 'title' in book and book['title']:
                response += f"   📖 العنوان: {sanitize_text(book['title'])}\n"

            # Author information
            if 'author_name' in book and book['author_name']:
                response += f"   ✍️ المؤلف: {sanitize_text(book['author_name'])}\n"
            elif 'name' in book and book['name']:  # Direct author name
                response += f"   ✍️ المؤلف: {sanitize_text(book['name'])}\n"

            # Publication details
            if 'isbn' in book and book['isbn']:
                response += f"   📋 ISBN: {book['isbn']}\n"
            if 'publication_date' in book and book['publication_date']:
                response += f"   📅 تاريخ النشر: {book['publication_date']}\n"
            if 'edition_number' in book and book['edition_number']:
                response += f"   📑 رقم الطبعة: {book['edition_number']}\n"

            # Content details
            if 'description' in book and book['description']:
                desc = sanitize_text(book['description'])
                if len(desc) > 150:
                    desc = desc[:147] + "..."
                response += f"   📝 الوصف: {desc}\n"

            # Statistics
            if 'pdf_page_count' in book and book['pdf_page_count']:
                response += f"   📄 عدد الصفحات: {book['pdf_page_count']}\n"
            if 'average_rating' in book and book['average_rating']:
                response += f"   ⭐ التقييم: {book['average_rating']}/5\n"
            if 'total_ratings' in book and book['total_ratings']:
                response += f"   👥 عدد التقييمات: {book['total_ratings']}\n"
            if 'download_count' in book and book['download_count']:
                response += f"   📥 مرات التحميل: {book['download_count']}\n"
            if 'bookmark_count' in book and book['bookmark_count']:
                response += f"   🔖 المفضلة: {book['bookmark_count']}\n"

            # Links
            if 'msarii_link' in book:
                response += f"   🔗 استكشف الكتاب: {book['msarii_link']}\n"
            elif 'title' in book:
                link = generate_msarii_link('book', book['title'])
                response += f"   🔗 استكشف الكتاب: {link}\n"

            if 'author_msarii_link' in book:
                response += f"   👤 صفحة المؤلف: {book['author_msarii_link']}\n"

            response += "\n"
    else:
        response = f"Found {len(results)} book(s):\n\n"

        for i, book in enumerate(results, 1):
            response += f"📚 **Book {i}:**\n"

            # Basic book info
            if 'title' in book and book['title']:
                response += f"   📖 Title: {sanitize_text(book['title'])}\n"

            # Author information
            if 'author_name' in book and book['author_name']:
                response += f"   ✍️ Author: {sanitize_text(book['author_name'])}\n"
            elif 'name' in book and book['name']:  # Direct author name
                response += f"   ✍️ Author: {sanitize_text(book['name'])}\n"

            # Publication details
            if 'isbn' in book and book['isbn']:
                response += f"   📋 ISBN: {book['isbn']}\n"
            if 'publication_date' in book and book['publication_date']:
                response += f"   📅 Published: {book['publication_date']}\n"
            if 'edition_number' in book and book['edition_number']:
                response += f"   📑 Edition: {book['edition_number']}\n"

            # Content details
            if 'description' in book and book['description']:
                desc = sanitize_text(book['description'])
                if len(desc) > 150:
                    desc = desc[:147] + "..."
                response += f"   📝 Description: {desc}\n"

            # Statistics
            if 'pdf_page_count' in book and book['pdf_page_count']:
                response += f"   📄 Pages: {book['pdf_page_count']}\n"
            if 'average_rating' in book and book['average_rating']:
                response += f"   ⭐ Rating: {book['average_rating']}/5\n"
            if 'total_ratings' in book and book['total_ratings']:
                response += f"   👥 Total Ratings: {book['total_ratings']}\n"
            if 'download_count' in book and book['download_count']:
                response += f"   📥 Downloads: {book['download_count']}\n"
            if 'bookmark_count' in book and book['bookmark_count']:
                response += f"   🔖 Bookmarks: {book['bookmark_count']}\n"

            # Links
            if 'msarii_link' in book:
                response += f"   🔗 Explore Book: {book['msarii_link']}\n"
            elif 'title' in book:
                link = generate_msarii_link('book', book['title'])
                response += f"   🔗 Explore Book: {link}\n"

            if 'author_msarii_link' in book:
                response += f"   👤 Author Page: {book['author_msarii_link']}\n"

            response += "\n"

    return response

def format_author_results(results, language="english"):
    """Format author-related results with Arabic support"""
    if language == "arabic":
        response = f"تم العثور على {len(results)} مؤلف/مؤلفين:\n\n"

        for i, author in enumerate(results, 1):
            response += f"✍️ **المؤلف {i}:**\n"

            if 'name' in author and author['name']:
                response += f"   الاسم: {sanitize_text(author['name'])}\n"
            if 'bio' in author and author['bio']:
                response += f"   السيرة الذاتية: {sanitize_text(author['bio'])}\n"
            if 'created_at' in author:
                response += f"   تاريخ الإضافة: {author['created_at']}\n"

            # Add msarii.com link
            if 'msarii_link' in author:
                response += f"   🔗 استكشف المزيد: {author['msarii_link']}\n"
            elif 'name' in author:
                link = generate_msarii_link('author', author['name'])
                response += f"   🔗 استكشف المزيد: {link}\n"

            response += "\n"
    else:
        response = f"Found {len(results)} author(s):\n\n"

        for i, author in enumerate(results, 1):
            response += f"✍️ **Author {i}:**\n"

            if 'name' in author and author['name']:
                response += f"   Name: {sanitize_text(author['name'])}\n"
            if 'bio' in author and author['bio']:
                response += f"   Biography: {sanitize_text(author['bio'])}\n"
            if 'created_at' in author:
                response += f"   Added: {author['created_at']}\n"

            # Add msarii.com link
            if 'msarii_link' in author:
                response += f"   🔗 Explore more: {author['msarii_link']}\n"
            elif 'name' in author:
                link = generate_msarii_link('author', author['name'])
                response += f"   🔗 Explore more: {link}\n"

            response += "\n"

    return response

def format_course_results(results, language="english"):
    """Format course-related results with Arabic support"""
    if language == "arabic":
        response = f"تم العثور على {len(results)} دورة/دورات:\n\n"

        for i, course in enumerate(results, 1):
            response += f"🎓 **الدورة {i}:**\n"

            if 'title' in course and course['title']:
                response += f"   العنوان: {sanitize_text(course['title'])}\n"
            if 'description' in course and course['description']:
                response += f"   الوصف: {sanitize_text(course['description'])}\n"
            if 'instructor' in course and course['instructor']:
                response += f"   المعلم: {sanitize_text(course['instructor'])}\n"
            if 'duration' in course and course['duration']:
                response += f"   المدة: {course['duration']}\n"
            if 'level' in course and course['level']:
                response += f"   المستوى: {course['level']}\n"

            # Add msarii.com link
            if 'msarii_link' in course:
                response += f"   🔗 استكشف المزيد: {course['msarii_link']}\n"
            elif 'title' in course:
                link = generate_msarii_link('course', course['title'])
                response += f"   🔗 استكشف المزيد: {link}\n"

            response += "\n"
    else:
        response = f"Found {len(results)} course(s):\n\n"

        for i, course in enumerate(results, 1):
            response += f"🎓 **Course {i}:**\n"

            if 'title' in course and course['title']:
                response += f"   Title: {sanitize_text(course['title'])}\n"
            if 'description' in course and course['description']:
                response += f"   Description: {sanitize_text(course['description'])}\n"
            if 'instructor' in course and course['instructor']:
                response += f"   Instructor: {sanitize_text(course['instructor'])}\n"
            if 'duration' in course and course['duration']:
                response += f"   Duration: {course['duration']}\n"
            if 'level' in course and course['level']:
                response += f"   Level: {course['level']}\n"

            # Add msarii.com link
            if 'msarii_link' in course:
                response += f"   🔗 Explore more: {course['msarii_link']}\n"
            elif 'title' in course:
                link = generate_msarii_link('course', course['title'])
                response += f"   🔗 Explore more: {link}\n"

            response += "\n"

    return response

def format_general_results(results, language="english"):
    """Format general results with Arabic support"""
    if language == "arabic":
        response = f"تم العثور على {len(results)} نتيجة/نتائج:\n\n"

        for i, result in enumerate(results, 1):
            response += f"📋 **النتيجة {i}:**\n"
            for key, value in result.items():
                if value is not None and key != 'msarii_link':
                    # Translate common field names to Arabic
                    field_translations = {
                        'id': 'المعرف',
                        'name': 'الاسم',
                        'title': 'العنوان',
                        'description': 'الوصف',
                        'created_at': 'تاريخ الإنشاء',
                        'updated_at': 'تاريخ التحديث'
                    }
                    field_name = field_translations.get(key, key.replace('_', ' '))
                    response += f"   {field_name}: {sanitize_text(value)}\n"

            # Add msarii link if available
            if 'msarii_link' in result:
                response += f"   🔗 استكشف المزيد: {result['msarii_link']}\n"

            response += "\n"
    else:
        response = f"Found {len(results)} result(s):\n\n"

        for i, result in enumerate(results, 1):
            response += f"📋 **Result {i}:**\n"
            for key, value in result.items():
                if value is not None and key != 'msarii_link':
                    response += f"   {key.replace('_', ' ').title()}: {sanitize_text(value)}\n"

            # Add msarii link if available
            if 'msarii_link' in result:
                response += f"   🔗 Explore more: {result['msarii_link']}\n"

            response += "\n"

    return response

# Simple test view without AutoGen
@method_decorator(csrf_exempt, name='dispatch')
class SimpleQueryView(APIView):
    def post(self, request):
        try:
            # Handle multiple content types and request methods
            question = None

            print(f"[DEBUG] Request method: {request.method}")
            print(f"[DEBUG] Content type: {request.content_type}")
            print(f"[DEBUG] Request data: {getattr(request, 'data', 'No data attr')}")
            print(f"[DEBUG] Request POST: {getattr(request, 'POST', 'No POST attr')}")

            # Try different ways to get the question
            if hasattr(request, 'data') and request.data and 'question' in request.data:
                question = request.data.get("question")
                print(f"[DEBUG] Got question from request.data: {question}")
            elif hasattr(request, 'POST') and 'question' in request.POST:
                question = request.POST.get("question")
                print(f"[DEBUG] Got question from request.POST: {question}")
            elif hasattr(request, 'body') and request.body:
                # Try to parse JSON from body
                try:
                    body_data = json.loads(request.body.decode('utf-8'))
                    question = body_data.get("question")
                    print(f"[DEBUG] Got question from JSON body: {question}")
                except Exception as e:
                    print(f"[DEBUG] Failed to parse JSON body: {e}")

            if not question:
                error_msg = {
                    "error": "Question is required",
                    "debug_info": {
                        "content_type": request.content_type,
                        "has_data": hasattr(request, 'data'),
                        "has_POST": hasattr(request, 'POST'),
                        "has_body": hasattr(request, 'body')
                    }
                }
                return Response(error_msg, status=status.HTTP_400_BAD_REQUEST)

            print(f"[INFO] Received question: {question}")

            # Detect query language
            query_language = detect_language(question)
            print(f"[INFO] Detected language: {query_language}")

            # COUNT mode (deterministic, no LLM)
            if detect_count_intent(question):
                schema = get_relevant_schema()
                entity_type = infer_entity_type(question)
                tables = get_tables_for_type(schema, entity_type) if entity_type else []
                if not tables:
                    tables = list(schema.keys())[:10] if schema else []
                counts = count_rows_in_tables(tables)
                formatted = format_count_response(counts, query_language, entity_type)
                # Add explanatory note for count mode
                note = "شرح: تم تحديد الجداول ذات الصلة من المخطط ثم حساب عدد الصفوف لكل جدول." if query_language == 'arabic' else "Explanation: Relevant tables were selected from the schema and row counts computed per table."
                combined = formatted + "\n\n" + note
                return Response({
                "response": combined,
                "success": True,
                "mode": "count",
                "tables_checked": tables
                }, status=status.HTTP_200_OK)

            # Comprehensive SQL queries based on keywords that fetch all relevant fields
            if "book" in question.lower() or "كتاب" in question:
                # Check if asking about specific book
                if "encyclopedia of science" in question.lower() or "موسوعة العلوم" in question:
                    sql = """
                    SELECT eb.*,
                           la.name as author_name, la.bio as author_bio, la.slug as author_slug
                    FROM library_encyclopedia_book eb
                    LEFT JOIN library_authors la ON eb.author_id = la.id
                    WHERE eb.title LIKE '%Encyclopedia of Science%'
                    """
                else:
                    sql = """
                    SELECT eb.*,
                           la.name as author_name, la.bio as author_bio, la.slug as author_slug
                    FROM library_encyclopedia_book eb
                    LEFT JOIN library_authors la ON eb.author_id = la.id
                    LIMIT 3
                    """
            elif "author" in question.lower() or "مؤلف" in question:
                if "Dr. Smith" in question or "smith" in question.lower():
                    sql = "SELECT * FROM library_authors WHERE name LIKE '%Smith%'"
                else:
                    sql = "SELECT * FROM library_authors LIMIT 3"
            else:
                # Default: show books with full details
                sql = """
                SELECT eb.*,
                       la.name as author_name, la.bio as author_bio, la.slug as author_slug
                FROM library_encyclopedia_book eb
                LEFT JOIN library_authors la ON eb.author_id = la.id
                LIMIT 2
                """

            print(f"[INFO] Executing SQL: {sql}")

            # Execute SQL
            sql_result = execute_sql_directly(sql)

            # Format response
            formatted_response = format_response_for_user(sql_result, query_language)

            return Response({
                "response": formatted_response,
                "executed_sql": sql,
                "success": sql_result.get("success", False),
                "result_count": sql_result.get("count", 0),
                "language": query_language
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"[ERROR] Simple query error: {e}")
            return Response({
                "response": f"❌ Error: {str(e)}",
                "success": False,
                "error": str(e)
            }, status=status.HTTP_200_OK)

# Simple Django view without DRF
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["POST"])
def simple_ai_query(request):
    """Simple AI query endpoint without DRF"""
    try:
        # Get question from POST data
        question = request.POST.get('question')

        if not question:
            # Try JSON body
            try:
                import json
                body_data = json.loads(request.body.decode('utf-8'))
                question = body_data.get('question')
            except:
                pass

        if not question:
            return JsonResponse({
                "error": "Question is required",
                "success": False
            }, status=400)

        print(f"[INFO] Received question: {question}")

        # Detect query language
        query_language = detect_language(question)
        print(f"[INFO] Detected language: {query_language}")

        # COUNT mode (deterministic, no LLM)
        if detect_count_intent(question):
            schema = get_relevant_schema()
            entity_type = infer_entity_type(question)
            tables = get_tables_for_type(schema, entity_type) if entity_type else []
            if not tables:
                tables = list(schema.keys())[:10] if schema else []
            counts = count_rows_in_tables(tables)
            formatted = format_count_response(counts, query_language, entity_type)
            return JsonResponse({
                "response": formatted,
                "success": True,
                "mode": "count",
                "tables_checked": tables
            })

        # Simple SQL query based on keywords
        if "book" in question.lower() or "كتاب" in question:
            # Check if asking about specific book
            if "encyclopedia of science" in question.lower() or "موسوعة العلوم" in question:
                sql = """
                SELECT eb.*,
                       la.name as author_name, la.bio as author_bio, la.slug as author_slug
                FROM library_encyclopedia_book eb
                LEFT JOIN library_authors la ON eb.author_id = la.id
                WHERE eb.title LIKE '%Encyclopedia of Science%'
                """
            else:
                sql = """
                SELECT eb.*,
                       la.name as author_name, la.bio as author_bio, la.slug as author_slug
                FROM library_encyclopedia_book eb
                LEFT JOIN library_authors la ON eb.author_id = la.id
                LIMIT 3
                """
        elif "author" in question.lower() or "مؤلف" in question:
            if "Dr. Smith" in question or "smith" in question.lower():
                sql = "SELECT * FROM library_authors WHERE name LIKE '%Smith%'"
            else:
                sql = "SELECT * FROM library_authors LIMIT 3"
        else:
            # Default: show books with full details
            sql = """
            SELECT eb.*,
                   la.name as author_name, la.bio as author_bio, la.slug as author_slug
            FROM library_encyclopedia_book eb
            LEFT JOIN library_authors la ON eb.author_id = la.id
            LIMIT 2
            """

        print(f"[INFO] Executing SQL: {sql}")

        # Execute SQL
        sql_result = execute_sql_directly(sql)

        # Format response
        formatted_response = format_response_for_user(sql_result, query_language)

        return JsonResponse({
            "response": formatted_response,
            "executed_sql": sql.replace('\n', ' ').replace('  ', ' '),
            "success": sql_result.get("success", False),
            "result_count": sql_result.get("count", 0),
            "language": query_language
        })

    except Exception as e:
        print(f"[ERROR] Simple query error: {e}")
        return JsonResponse({
            "response": f"❌ Error: {str(e)}",
            "success": False,
            "error": str(e)
        }, status=500)

class AIQueryView(APIView):
    def post(self, request):
        try:
            # Handle both JSON and form data
            if hasattr(request, 'data') and request.data:
                question = request.data.get("question")
            else:
                question = request.POST.get("question")

            if not question:
                return Response({"error": "Question is required"}, status=status.HTTP_400_BAD_REQUEST)

            print(f"[INFO] Received question: {question}")

            # Detect query language
            query_language = detect_language(question)
            print(f"[INFO] Detected language: {query_language}")

            # COUNT mode (deterministic, no LLM)
            if detect_count_intent(question):
                schema = get_relevant_schema()
                entity_type = infer_entity_type(question)
                tables = get_tables_for_type(schema, entity_type) if entity_type else []
                if not tables:
                    tables = list(schema.keys())[:10] if schema else []
                counts = count_rows_in_tables(tables)
                formatted = format_count_response(counts, query_language, entity_type)
                return Response({
                    "response": formatted,
                    "success": True,
                    "mode": "count",
                    "tables_checked": tables
                }, status=status.HTTP_200_OK)

            # Fetch schema and build enhanced prompt
            schema = get_relevant_schema()
            prompt_template = generate_enhanced_prompt(schema, question)

            # Container for final response from agent
            captured_response = {"content": ""}

            # Capture callback for content
            def capture_callback(agent, message):
                print(f"[DEBUG] Agent message: {message}")
                if "content" in message:
                    captured_response["content"] = message["content"]

            # If AutoGen isn't ready, fall back to direct SQL path
            if not (AUTOGEN_AVAILABLE and GROQ_API_KEY):
                # Use dynamic schema-aware fallback for better accuracy
                dynamic_sql = None
                # Prefer pattern-based author detection (e.g., من هو ...)
                if infer_entity_type_from_patterns(question) == 'author' or infer_entity_type(question) == 'author':
                    dynamic_sql = build_dynamic_author_sql(schema, question)
                elif ("book" in (question or "").lower()) or ("كتاب" in (question or "")):
                    dynamic_sql = build_dynamic_book_sql(schema, question)
                # Fallback heuristics if dynamic build not possible
                if not dynamic_sql:
                    if "book" in question.lower() or "كتاب" in question:
                        if "encyclopedia of science" in question.lower() or "موسوعة العلوم" in question:
                            dynamic_sql = (
                                "SELECT eb.*, la.name as author_name, la.bio as author_bio, la.slug as author_slug "
                                "FROM library_encyclopedia_book eb LEFT JOIN library_authors la ON eb.author_id = la.id "
                                "WHERE eb.title LIKE '%Encyclopedia of Science%'"
                            )
                        else:
                            dynamic_sql = (
                                "SELECT eb.*, la.name as author_name, la.bio as author_bio, la.slug as author_slug "
                                "FROM library_encyclopedia_book eb LEFT JOIN library_authors la ON eb.author_id = la.id "
                                "LIMIT 3"
                            )
                    elif "author" in question.lower() or "مؤلف" in question:
                        dynamic_sql = "SELECT * FROM library_authors LIMIT 5"
                    else:
                        dynamic_sql = (
                            "SELECT eb.*, la.name as author_name, la.bio as author_bio, la.slug as author_slug "
                            "FROM library_encyclopedia_book eb LEFT JOIN library_authors la ON eb.author_id = la.id "
                            "LIMIT 2"
                        )

                sql_result = execute_sql_directly(dynamic_sql)
                formatted_response = format_response_for_user(sql_result, query_language)
                explanation = build_explanation_note(dynamic_sql, query_language)
                combined = formatted_response + "\n\n" + explanation if formatted_response else explanation

                return Response({
                    "response": combined,
                    "executed_sql": dynamic_sql,
                    "success": sql_result.get("success", False),
                    "result_count": sql_result.get("count", 0),
                    "language": query_language,
                    "note": "AutoGen disabled; used schema-aware fallback"
                }, status=status.HTTP_200_OK)

            # Start interaction when AutoGen is available
            user_proxy.initiate_chat(sql_writer, message=prompt_template, callback=capture_callback)

            # Process the response
            content = captured_response["content"].strip()

            if not content:
                error_msg = "No response was generated by the agent." if query_language == "english" else "لم يتم إنتاج استجابة من الوكيل."
                return Response(
                    {"response": error_msg, "details": None},
                    status=status.HTTP_200_OK
                )

            # Extract SQL from the agent's response
            sql_query = extract_sql_from_response(content)

            if sql_query:
                print(f"[INFO] Extracted SQL: {sql_query}")

                # Execute the SQL query directly
                sql_result = execute_sql_directly(sql_query)
                
                # Format the response for the user with language support
                formatted_response = format_response_for_user(sql_result, query_language)
                # Append explanation note about SQL/tables used
                explanation = build_explanation_note(sql_query, query_language)
                combined = formatted_response + "\n\n" + explanation if formatted_response else explanation
                
                return Response({
                "response": combined,
                "raw_sql_response": content,
                "executed_sql": sql_query,
                "success": True,
                "result_count": sql_result.get("count", 0),
                "language": query_language
                }, status=status.HTTP_200_OK)
            else:
                # If no SQL found, check if there's an error in the content
                if "error" in content.lower() or "failed" in content.lower():
                    error_prefix = "❌ خطأ في الوكيل الذكي:" if query_language == "arabic" else "❌ AI Agent Error:"
                    return Response({
                        "response": f"{error_prefix} {content}",
                        "success": False,
                        "note": "AI agent encountered an error",
                        "language": query_language
                    }, status=status.HTTP_200_OK)
                else:
                    # Return the raw agent response
                    note_text = "No SQL query could be extracted from the response" if query_language == "english" else "لم يتم استخراج استعلام SQL من الاستجابة"
                    return Response({
                        "response": content,
                        "success": True,
                        "note": note_text,
                        "language": query_language
                    }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"[ERROR] AI Agent error: {e}")
            # Detect language for error handling
            try:
                error_query_language = detect_language(question)
            except:
                error_query_language = "english"

            # Try to extract SQL from error messages
            error_content = str(e)
            sql_query = extract_sql_from_response(error_content)

            if sql_query:
                print(f"[INFO] Extracted SQL from error: {sql_query}")
                sql_result = execute_sql_directly(sql_query)
                formatted_response = format_response_for_user(sql_result, error_query_language)

                return Response({
                    "response": formatted_response,
                    "raw_error": error_content,
                    "executed_sql": sql_query,
                    "success": True,
                    "result_count": sql_result.get("count", 0),
                    "language": error_query_language
                }, status=status.HTTP_200_OK)
            else:
                error_prefix = "❌ خطأ في الوكيل الذكي:" if error_query_language == "arabic" else "❌ AI Agent Error:"
                note_text = "AI agent encountered an error and no SQL could be extracted" if error_query_language == "english" else "واجه الوكيل الذكي خطأ ولم يتم استخراج استعلام SQL"
                return Response({
                    "response": f"{error_prefix} {error_content}",
                    "success": False,
                    "note": note_text,
                    "language": error_query_language
                }, status=status.HTTP_200_OK)

class TestDatabaseView(APIView):
    """Test endpoint to check database connectivity and see available data"""
    def get(self, request):
        try:
            results = {}
            
            with connections['default'].cursor() as cursor:
                # Get all tables depending on DB vendor
                vendor = connections['default'].vendor
                if vendor == 'sqlite':
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    existing_tables = [row[0] for row in cursor.fetchall()]
                else:
                    cursor.execute("SHOW TABLES;")
                    existing_tables = [row[0] for row in cursor.fetchall()]
                
                print(f"[DEBUG] Found tables: {existing_tables}")
                
                for table in existing_tables:
                    try:
                        # Get table structure depending on DB vendor
                        vendor = connections['default'].vendor
                        if vendor == 'sqlite':
                            cursor.execute(f"PRAGMA table_info({table});")
                            columns = cursor.fetchall()
                        else:
                            cursor.execute(f"DESCRIBE {table};")
                            columns = cursor.fetchall()
                        
                        # Get sample data (first 5 rows)
                        cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
                        sample_data = cursor.fetchall()
                        
                        # Get column names
                        column_names = [desc[0] for desc in cursor.description]
                        
                        # Format sample data
                        formatted_data = []
                        for row in sample_data:
                            row_dict = {}
                            for i, value in enumerate(row):
                                row_dict[column_names[i]] = value
                            formatted_data.append(row_dict)
                        
                        # Map columns representation for response
                        if vendor == 'sqlite':
                            column_meta = [{"name": col[1], "type": col[2]} for col in columns]
                        else:
                            column_meta = [{"name": col[0], "type": col[1]} for col in columns]

                        results[table] = {
                            "columns": column_meta,
                            "sample_data": formatted_data,
                            "row_count": len(formatted_data)
                        }
                        
                    except Exception as e:
                        results[table] = {
                            "error": str(e),
                            "columns": [],
                            "sample_data": [],
                            "row_count": 0
                        }
            
            return Response({
                "database_status": "connected",
                "available_tables": existing_tables,
                "total_tables": len(existing_tables),
                "tables": results
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                "database_status": "error",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.shortcuts import render

class AIInterfaceView:
    """View to serve the AI interface HTML page"""
    def __call__(self, request):
        return render(request, 'ai_interface.html')


