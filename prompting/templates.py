"""
Industry-Specific Decision & Strategy Template Library for Debate-Club.
Provides battle-tested motions, objectives, and recommended model configurations
for Tech Architecture, Executive Strategy, Finance & Risk, and Legal & Policy.
"""

from typing import List, Dict, Any

DECISION_TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "🏗️ Tech & Architecture": [
        {
            "title": "Modular Monolith vs Microservices Architecture",
            "mode": "plan",
            "question": "Architect the core backend for a high-growth B2B fintech platform: Modular Monolith vs Distributed Microservices. Detail scaling trade-offs, deployment complexity, and database boundary strategy.",
            "recommended_engines": 3,
            "recommended_rounds": 3,
            "tags": ["Engineering", "Fintech", "Cloud"]
        },
        {
            "title": "PostgreSQL vs DynamoDB / NoSQL for Real-Time Event Streams",
            "mode": "debate",
            "question": "For a real-time event analytics platform handling 50,000 writes/sec, should we adopt partitioned PostgreSQL with TimescaleDB or Amazon DynamoDB + OpenSearch?",
            "recommended_engines": 3,
            "recommended_rounds": 3,
            "tags": ["Databases", "Scalability", "Data Engine"]
        },
        {
            "title": "Kubernetes Cluster vs Pure Serverless on AWS/GCP",
            "mode": "plan",
            "question": "Design an automated deployment infrastructure for an AI-native SaaS application: EKS/GKE Kubernetes cluster vs Fully Managed Serverless (Cloud Run / AWS Lambda).",
            "recommended_engines": 2,
            "recommended_rounds": 3,
            "tags": ["DevOps", "Infrastructure", "Cost"]
        },
        {
            "title": "Python FastAPI vs Rust Actix for High-Throughput Inference Gateway",
            "mode": "debate",
            "question": "Should our high-concurrency LLM routing proxy be written in Python (FastAPI + AsyncIO) for developer speed or Rust (Actix-web / Tokio) for raw memory and throughput efficiency?",
            "recommended_engines": 2,
            "recommended_rounds": 3,
            "tags": ["Performance", "Languages", "Backend"]
        }
    ],
    "🚀 Executive & Product Strategy": [
        {
            "title": "B2B AI Agent SaaS: Freemium vs Sales-Led Enterprise Model",
            "mode": "plan",
            "question": "Formulate the go-to-market and monetization strategy for an enterprise autonomous agent tool: Self-Serve Product-Led Growth (PLG) vs High-Touch Enterprise Sales-Led Model.",
            "recommended_engines": 3,
            "recommended_rounds": 3,
            "tags": ["GTM", "Monetization", "SaaS"]
        },
        {
            "title": "Build Proprietary Core AI Model vs Fine-Tune Open Source (Llama/Qwen)",
            "mode": "debate",
            "question": "Should a vertical legal-tech startup pre-train/fine-tune proprietary open-weight models (Llama 3.3 / Qwen 2.5) or build on top of frontier APIs (Claude 3.5 Sonnet / GPT-4o)?",
            "recommended_engines": 3,
            "recommended_rounds": 3,
            "tags": ["AI Strategy", "Economics", "Moat"]
        },
        {
            "title": "Pricing Architecture: Usage-Based Token Billing vs Flat Seat Subscriptions",
            "mode": "plan",
            "question": "Design a sustainable pricing structure for an AI copilot platform: Consumption-based credit metering vs Flat monthly per-seat licensing.",
            "recommended_engines": 2,
            "recommended_rounds": 3,
            "tags": ["Pricing", "Finance", "Product"]
        },
        {
            "title": "Global Launch Red-Teaming: Mitigating Brand, Legal & Security Risks",
            "mode": "plan",
            "question": "Stress-test and red-team our upcoming global product launch: identify catastrophic edge cases, compliance roadblocks (GDPR/EU AI Act), and PR disaster scenarios with concrete mitigations.",
            "recommended_engines": 3,
            "recommended_rounds": 3,
            "tags": ["Risk", "Compliance", "Red Team"]
        }
    ],
    "📈 Finance, Crypto & Macro": [
        {
            "title": "Bull vs Bear Case: Sustained ROI on Multi-Billion AI Datacenter CapEx",
            "mode": "debate",
            "question": "Will the ongoing $500B+ hyper-scaler data center and GPU CapEx cycle yield positive macroeconomic ROI by 2028, or lead to a severe over-capacity crash?",
            "recommended_engines": 3,
            "recommended_rounds": 4,
            "tags": ["Macro", "Semiconductors", "Investments"]
        },
        {
            "title": "Startup Financing: Institutional VC Round vs Cashflow Bootstrapping",
            "mode": "debate",
            "question": "For a profitable B2B AI tooling startup with $1M ARR, is raising a $5M Series A institutional venture round superior to organic cashflow bootstrapping?",
            "recommended_engines": 2,
            "recommended_rounds": 3,
            "tags": ["Startups", "Venture Capital", "Growth"]
        },
        {
            "title": "Hedging Strategy for Floating Interest Rates & FX Volatility",
            "mode": "plan",
            "question": "Design a treasury and risk management strategy for a mid-market global manufacturing business to hedge against sustained high interest rates and currency fluctuations.",
            "recommended_engines": 3,
            "recommended_rounds": 3,
            "tags": ["Treasury", "Risk", "Finance"]
        }
    ],
    "⚖️ Legal, Policy & Ethics": [
        {
            "title": "Open-Source AI Compute Thresholds & Safety Regulation",
            "mode": "debate",
            "question": "Should governments impose mandatory licensing and security audits on open-weight AI model weights exceeding 10^26 FLOPs compute training budgets?",
            "recommended_engines": 3,
            "recommended_rounds": 3,
            "tags": ["Policy", "Safety", "Governance"]
        },
        {
            "title": "Autonomous Agent Liability: Platform vs End-User Responsibility",
            "mode": "debate",
            "question": "When an autonomous AI agent executes a catastrophic financial trade or unauthorized data deletion, should legal liability rest with the platform developer or the operating user?",
            "recommended_engines": 2,
            "recommended_rounds": 3,
            "tags": ["Law", "Liability", "Contracts"]
        },
        {
            "title": "AI Training on Public Copyrighted Web Data & Fair Use",
            "mode": "debate",
            "question": "Does scraping public internet content to train commercial foundation models constitute transformative Fair Use under US and international copyright law?",
            "recommended_engines": 3,
            "recommended_rounds": 3,
            "tags": ["Copyright", "IP", "Legal"]
        }
    ]
}


def get_all_template_categories() -> List[str]:
    return list(DECISION_TEMPLATES.keys())


def get_templates_for_category(category: str) -> List[Dict[str, Any]]:
    return DECISION_TEMPLATES.get(category, [])
