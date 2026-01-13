🌍 People of Anioma


People of Anioma is a cultural intelligence and storytelling platform dedicated to preserving, analyzing, and amplifying the history, identity, and lived experiences of the Anioma people.


It combines editorial publishing, community narratives, ethnographic research, geospatial visualization, and real-time media intelligence into a single, scalable system.


This is not just a content site.
It is a cultural data and intelligence platform.



🌱 Why This Matters

Anioma history, identity, and lived experience exist largely in fragmented memories, oral traditions, scattered records, and fleeting online conversations. Much of this knowledge is undocumented, unindexed, or lost to time, platform decay, and generational gaps.

People of Anioma exists to change that.


This project treats culture not as static folklore, but as living data:
   Stories being told today
   Migrations happening now
   Debates unfolding online
   Traditions adapting in real time


By combining storytelling, research, technology, and intelligence, the platform creates a durable record of Anioma life — past, present, and emerging.

What We Are Protecting

Oral histories before they disappear
Community narratives before they are diluted
Cultural context before it is misrepresented
Local voices before they are drowned out



What We Are Enabling

Future historians to work with structured cultural data
Researchers to analyze trends, language, and movement
Communities to see themselves reflected accurately
Editors to respond intelligently to how Anioma is portrayed



A Different Philosophy
Most platforms focus on content delivery.
This project focuses on cultural continuity.

Most systems scrape information.
This system understands it.

Most archives preserve the past.
This platform captures the present for the future.

Culture survives when it is remembered.
It thrives when it is understood.



✨ Core Capabilities
Long-form articles & video publishing
Community stories & oral histories
Ethnographic surveys with NLP analysis
Diaspora tracking & migration analytics
Interactive cultural maps
Newsletter & community updates
Real-time Anioma media monitoring & alerts



🧠 Key Applications

Blog & Video Platform
Editorial articles and multimedia posts
Video publishing via direct S3 uploads (presigned URLs)
Reactions, comments, view tracking
Category-based discovery


Stories (Community Narratives)
User-submitted stories and oral histories
Moderation workflow
Global feed + personal dashboards
Engagement analytics


Ethnographic Survey Engine
Structured cultural data collection
NLP analysis:
   Text summaries
   Keyword extraction
   Topic modeling
   Research dashboards & data export



Diaspora Tracker
Migration origin/destination tracking
Motivation analysis
Interactive maps (Leaflet + GeoJSON)
Research-ready datasets


Cultural Maps (maps)
Clan, origin, and settlement visualization
Spatial storytelling
Integrated with survey & diaspora data


Pages (pages)
CMS-style institutional content
About, policies, cultural explainers
Stable, non-ephemeral content layer


Newsletter (newsletter)
Subscriber management
AJAX-based footer signup
Community updates & announcements



Media Intelligence 🛰️
Monitors websites and social platforms
Detects Anioma-related content semantically
Scores relevance, confidence, sentiment & severity
Deduplicates content at ingestion
Editorial controls & overrides
Smart notifications (Telegram)
Breaking-news override logic

🧠 Intelligence is the product.

🧱 System Architecture
High-Level Overview

┌─────────────────────┐
│  External Platforms │
│  (Web, Social, СМИ) │
└─────────┬───────────┘
          │
          ▼
┌──────────────────────────┐
│ Media Intelligence Layer │
│ - Platform Monitors      │
│ - Semantic Analysis      │
│ - Deduplication          │
│ - Scoring & Severity     │
└─────────┬────────────────┘
          │
          ▼
┌──────────────────────────┐
│ Django Core Applications │
│                          │
│ Blog / Videos            │
│ Stories                  │
│ Surveys                  │
│ Diaspora Tracker         │
│ Maps                     │
│ Pages                    │
│ Newsletter               │
└─────────┬────────────────┘
          │
          ▼
┌──────────────────────────┐
│ Data & Intelligence      │
│ - PostgreSQL             │
│ - GeoJSON                │
│ - NLP Models             │
└─────────┬────────────────┘
          │
          ▼
┌──────────────────────────┐
│ Notification Layer       │
│ - Telegram Alerts        │
│ - Editorial Overrides    │
│ - Rate Limiting          │
└──────────────────────────┘



🧠 Design Principles

Intelligence-first
Strong deduplication guarantees
Editorial control over automation
Optional dependencies (safe imports)
Production-safe media handling
Research-friendly data models



🚀 Deployment
Backend: Django
Database: PostgreSQL
Media storage: AWS S3
NLP: NLTK / Gensim / scikit-learn
Maps: Leaflet + GeoJSON
Notifications: Telegram Bot API
Hosting: Render




📚 Intended Use
Cultural preservation
Academic & ethnographic research
Community storytelling
Editorial monitoring
Historical archiving


🤝 Contributing
This project is under active development.
Contributions, reviews, and research collaborations are welcome.