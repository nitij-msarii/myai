# Arabic Library AI Agent (SQLite-ready, environment-based secrets)

## Overview
This project provides an Arabic-first AI agent for querying a library domain (books, authors, categories, articles, webapps, and companies) and producing contextual responses with SEO-friendly links to msarii.com. It supports:
- Arabic intent detection and smart query parsing
- Data retrieval via Django ORM (EnhancedAIAgent) or SQL (API endpoints)
- Dynamic link generation with Arabic slugs
- SQLite by default for development, with cross-database schema introspection (SQLite/MySQL compatible)
- No secrets committed to code; GROQ API key is read from environment variables

## Key Components
- EnhancedAIAgent (AI_agent/enhanced_agent.py)
  - Pure-Python/Django ORM agent that understands Arabic queries and fetches data from Enhanced models
- Link Generator (AI_agent/link_generator.py)
  - Builds msarii.com URLs and structured responses with related links
- Enhanced Models (AI_agent/enhanced_models.py)
  - Models for EnhancedAuthor, EnhancedBook, Category, Article, WebApp, Company
- API Views (AI_agent/views.py)
  - simple_ai_query (POST /ai/query): simple, heuristic SQL
  - SimpleQueryView (POST /ai/query-drf/): same, via DRF
  - AIQueryView (POST /ai/query-full/): uses schema reflection and (optionally) an LLM (Groq) to produce SQL; falls back to heuristic SQL when no LLM key is present
  - TestDatabaseView (GET /ai/test-db/): lists tables, columns, and sample rows (supports SQLite and MySQL)

## Database
- Default DB is SQLite (configured in myAI/settings.py)
- Enhanced models have migrations and a population script with Arabic sample data

### Initialize DB
```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py populate_enhanced_data
```

This will create Arabic authors, books, categories, articles, etc.

## Secrets (GROQ API key)
GROQ_API_KEY is NOT hard-coded anywhere. The app reads it only from environment variables.

Set it on your system before running the full LLM-powered endpoint:
- Windows (PowerShell):
```
setx GROQ_API_KEY "your-groq-api-key"
```
- macOS/Linux (bash):
```
export GROQ_API_KEY=your-groq-api-key
```

Note: .env is ignored by git (.gitignore includes .env). If you want automatic .env loading, you can add python-dotenv and load it in settings; otherwise, stick to environment variables.

## Run Server
```
python manage.py runserver
```

## Endpoints
- Simple (no LLM): POST /ai/query
- Simple (DRF): POST /ai/query-drf/
- Full (LLM-backed when GROQ_API_KEY is set, else fallback): POST /ai/query-full/
- DB Introspection: GET /ai/test-db/

### Example Requests
- Simple form-encoded Arabic book query
```
curl -X POST -d "question=أريد معلومات عن كتاب الروح" http://127.0.0.1:8000/ai/query
```

- DRF JSON author query
```
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "من هو ابن قيم الجوزية"}' \
  http://127.0.0.1:8000/ai/query-drf/
```

- Full LLM (requires GROQ_API_KEY)
```
curl -X POST -H "Content-Type: application/json" \
  -d '{"question": "أريد كتب الفقه الإسلامي"}' \
  http://127.0.0.1:8000/ai/query-full/
```

## How the agents respond to queries

There are two main paths:

1) EnhancedAIAgent (pure ORM, used in tests and can be used in code)
- Normalization: cleans Arabic punctuation and whitespace
- Intent routing (Arabic-aware):
  - Books: detects كتاب/كتب. If it matches “كتب <category>” pattern, routes to category handler
  - Authors: detects مؤلف/كاتب/عالم or the pattern "من هو <name>"
  - Categories: detects فئة/تصنيف/نوع
  - Articles: detects مقال/مقالات/بحث
  - Webapps: detects تطبيق/تطبيقات/برنامج/برامج
  - Companies: detects شركة/شركات/مؤسسة
- Search text extraction: removes common Arabic stopwords and intent words (e.g., "أريد", "عن", "من هو", "كتاب", ...), then searches the corresponding models by name/title/content
- Response building: returns structured JSON with fields and dynamic links. For books, includes links to the book page, author page, and related books by the same author. For authors, includes their books and articles with links. For categories, includes books under that category
- Suggestions: when no exact match is found, returns suggestions for similar authors/books/categories

Example outcomes (with sample data):
- "أريد معلومات عن كتاب الروح" → Book details for الروح + links (book, author, related)
- "من هو ابن قيم الجوزية" → Author profile, with links to author page, their books and articles
- "أريد كتب الفقه الإسلامي" → Category response (الفقه الإسلامي) + books in that category
- "مقالات عن الفكر الإسلامي" → Article response with author link

2) API Endpoints (SQL-based)
- The simple endpoints (/ai/query and /ai/query-drf/) use keyword heuristics to build a SELECT that joins books with authors or lists authors; results are formatted with Arabic labels and enriched with msarii.com links (book/author/article/company/webapp) when applicable
- The full endpoint (/ai/query-full/) first reflects the DB schema in a DB-vendor-aware way:
  - SQLite: SELECT name FROM sqlite_master ... + PRAGMA table_info
  - MySQL: SHOW TABLES; + DESCRIBE <table>
- With GROQ_API_KEY present and AutoGen available, it sends an instruction prompt including the schema and lets the agent choose the correct SELECT; otherwise, it falls back to the same heuristic SQL as the simple endpoints
- In all cases, the results are formatted for the user with Arabic or English labels depending on the detected language of the question, and links are generated based on the row fields

## Link Generation
- For Enhanced models, each entity exposes get_msarii_url or is mapped to a base path:
  - Authors: https://msarii.com/authors/{slug}
  - Books: https://msarii.com/book-detail/{slug}
  - Categories: https://msarii.com/categories/{slug}
  - Articles: https://msarii.com/articles/{slug}
  - WebApps: https://msarii.com/webapps/detail/{slug}
  - Companies: https://msarii.com/webapps/companies/{slug}
- Arabic slugs are normalized (diacritics removed and ASCII transliteration for certain paths) to keep URLs SEO-friendly; Arabic author slugs can be preserved where available

## Testing
- Enhanced agent functional test:
```
python test_enhanced_agent.py
```
- Link generation and URL structure:
```
python test_link_generation.py
```
- Database exploration via API:
```
curl http://127.0.0.1:8000/ai/test-db/
```

## Troubleshooting
- If migrations fail, ensure Django is installed per requirements.txt and run makemigrations/migrate again
- If /ai/query-full returns a fallback note, check that GROQ_API_KEY is set in your environment
- If a specific Arabic query returns no results, confirm the sample data contains the same lemma/word form (e.g., "تعليمية" vs "التعليم") or extend normalization rules in the agent

## Security and Secrets
- No API keys are committed to source. GROQ_API_KEY is read from environment only
- .env is included in .gitignore. If you use a .env in development, it won’t be pushed to git

## Notes
- Default DB is SQLite; the project’s schema reflection and test endpoints support both SQLite and MySQL
- For production, configure your environment variables and database settings as needed