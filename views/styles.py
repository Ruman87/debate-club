"""
CSS Styles and Aesthetic Tokens for Debate-Club UI.
"""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.main-header {
    text-align: center;
    padding: 1.5rem 0 1rem 0;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.main-title {
    font-size: 2.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60A5FA 0%, #A78BFA 50%, #F472B6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
}

.subtitle {
    font-size: 1.05rem;
    color: #94A3B8;
    max-width: 700px;
    margin: 0 auto;
}

/* Card Styling */
.debate-card {
    background: rgba(30, 41, 59, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.25rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.debate-card:hover {
    border-color: rgba(147, 197, 253, 0.3);
}

/* Header badge inside card */
.debater-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.debater-badge {
    font-size: 0.95rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.score-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 8px;
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.3);
}

/* Sections inside card */
.section-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    color: #94A3B8;
    margin-top: 0.6rem;
    margin-bottom: 0.3rem;
}

.rebuttal-box {
    background: rgba(239, 68, 68, 0.08);
    border-left: 3px solid #EF4444;
    padding: 0.6rem 0.9rem;
    border-radius: 0 8px 8px 0;
    font-size: 0.92rem;
    margin-bottom: 0.6rem;
    color: #FCA5A5;
}

.agreement-chip {
    display: inline-block;
    background: rgba(16, 185, 129, 0.12);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.25);
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.82rem;
    margin-right: 6px;
    margin-bottom: 4px;
}

.answer-box {
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.95rem;
    line-height: 1.5;
    color: #E2E8F0;
}

/* =========================================================
   GRAPHIC NOVEL / COMIC SPEECH BALLOON & CHARACTER STYLES
   ========================================================= */

.comic-timeline {
    display: flex;
    flex-direction: column;
    gap: 1.75rem;
    margin: 1.5rem 0;
}

.comic-turn-row {
    display: flex;
    align-items: flex-start;
    gap: 1.25rem;
    width: 100%;
}

.comic-turn-row.row-left {
    flex-direction: row;
}

.comic-turn-row.row-right {
    flex-direction: row-reverse;
}

.comic-avatar-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 96px;
    max-width: 110px;
    text-align: center;
    flex-shrink: 0;
}

.comic-avatar-frame {
    width: 82px;
    height: 82px;
    border-radius: 50%;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #1E293B;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.comic-avatar-frame img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.comic-avatar-nameplate {
    font-weight: 800;
    font-size: 0.92rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-top: 6px;
    line-height: 1.2;
}

.comic-avatar-model {
    font-size: 0.72rem;
    color: #94A3B8;
    background: rgba(255, 255, 255, 0.06);
    padding: 1px 6px;
    border-radius: 4px;
    margin-top: 3px;
    max-width: 100px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

/* Comic Speech Balloons */
.comic-balloon {
    position: relative;
    flex: 1;
    background: rgba(26, 32, 44, 0.95);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 1.25rem 1.4rem;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    transition: border-color 0.2s ease, transform 0.2s ease;
}

.comic-balloon:hover {
    transform: translateY(-2px);
}

/* Speech Balloon Pointer Tails */
.comic-tail-left {
    position: absolute;
    top: 28px;
    left: -12px;
    width: 0;
    height: 0;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
    border-right: 12px solid var(--balloon-border-color, #3B82F6);
}

.comic-tail-right {
    position: absolute;
    top: 28px;
    right: -12px;
    width: 0;
    height: 0;
    border-top: 10px solid transparent;
    border-bottom: 10px solid transparent;
    border-left: 12px solid var(--balloon-border-color, #8B5CF6);
}

/* Header inside balloon */
.balloon-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.balloon-speaker-title {
    font-size: 0.95rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 6px;
}

.balloon-turn-pill {
    font-size: 0.76rem;
    font-weight: 600;
    color: #94A3B8;
    background: rgba(255, 255, 255, 0.08);
    padding: 2px 8px;
    border-radius: 12px;
    margin-left: 6px;
}

.balloon-agreement-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 8px;
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.3);
}

.balloon-speech-text {
    font-size: 1.02rem;
    line-height: 1.6;
    color: #F8FAFC;
    margin-bottom: 0.9rem;
    letter-spacing: -0.01em;
}

/* Critique & Rebuttal Box */
.comic-critique-block {
    background: rgba(239, 68, 68, 0.08);
    border-left: 3.5px solid #EF4444;
    border-radius: 0 10px 10px 0;
    padding: 0.7rem 1rem;
    margin-bottom: 0.75rem;
    font-size: 0.92rem;
    line-height: 1.5;
    color: #FECACA;
}

.comic-critique-header {
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #F87171;
    margin-bottom: 0.3rem;
    display: flex;
    align-items: center;
    gap: 5px;
}

/* Agreement Chips */
.comic-agreed-block {
    margin-bottom: 0.75rem;
}

.comic-agreed-header {
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #34D399;
    margin-bottom: 0.35rem;
    display: flex;
    align-items: center;
    gap: 5px;
}

.comic-agreed-chip {
    display: inline-block;
    background: rgba(16, 185, 129, 0.12);
    color: #6EE7B7;
    border: 1px solid rgba(16, 185, 129, 0.3);
    padding: 3px 9px;
    border-radius: 6px;
    font-size: 0.82rem;
    margin-right: 6px;
    margin-bottom: 4px;
}

/* Comic Thought Bubble */
.comic-thought-bubble {
    background: rgba(30, 41, 59, 0.55);
    border: 1.5px dashed rgba(148, 163, 184, 0.35);
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin-top: 0.6rem;
    font-style: italic;
    font-size: 0.88rem;
    color: #CBD5E1;
    line-height: 1.45;
}

/* =========================================================
   MAIN STAGE PHOTO WITH DYNAMIC OVERLAID SPEECH BALLOONS
   ========================================================= */

.stage-photo-wrapper {
    position: relative;
    width: 100%;
    max-width: 980px;
    margin: 0 auto 1.5rem auto;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 16px 44px rgba(0, 0, 0, 0.6);
    border: 2px solid rgba(255, 255, 255, 0.15);
    background: #0B0F19;
}

.stage-photo-img {
    width: 100%;
    height: auto;
    display: block;
}

/* Overlaid Graphic Novel Speech Balloon */
.stage-overlay-balloon {
    position: absolute;
    z-index: 20;
    background: #FFFFFF;
    color: #0F172A;
    border-radius: 22px;
    padding: 12px 18px;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.65), 0 0 0 1px rgba(0, 0, 0, 0.08);
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    animation: popBalloon 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes popBalloon {
    0% { transform: scale(0.85) translateY(10px); opacity: 0; }
    100% { transform: scale(1) translateY(0); opacity: 1; }
}

/* Position for Debater 1: Alex (Left Podium) */
.stage-overlay-balloon.balloon-alex {
    top: 5%;
    left: 4%;
    width: 45%;
    max-width: 440px;
    border: 3.5px solid #3B82F6;
}

.stage-tail-alex {
    position: absolute;
    bottom: -16px;
    left: 26%;
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-top: 16px solid #3B82F6;
}

.stage-tail-alex-inner {
    position: absolute;
    bottom: -11px;
    left: 26%;
    width: 0;
    height: 0;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    border-top: 12px solid #FFFFFF;
}

/* Position for Debater 2: Charlie (Center Podium) */
.stage-overlay-balloon.balloon-charlie {
    top: 5%;
    left: 28%;
    width: 45%;
    max-width: 440px;
    border: 3.5px solid #A855F7;
}

.stage-tail-charlie {
    position: absolute;
    bottom: -16px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-top: 16px solid #A855F7;
}

.stage-tail-charlie-inner {
    position: absolute;
    bottom: -11px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    border-top: 12px solid #FFFFFF;
}

/* Position for Debater 3: Shahar / Sam (Right Podium) */
.stage-overlay-balloon.balloon-sam,
.stage-overlay-balloon.balloon-shahar {
    top: 5%;
    right: 4%;
    width: 45%;
    max-width: 440px;
    border: 3.5px solid #EF4444;
}

.stage-tail-sam,
.stage-tail-shahar {
    position: absolute;
    bottom: -16px;
    right: 26%;
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-top: 16px solid #EF4444;
}

.stage-tail-sam-inner,
.stage-tail-shahar-inner {
    position: absolute;
    bottom: -11px;
    right: 26%;
    width: 0;
    height: 0;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    border-top: 12px solid #FFFFFF;
}

/* Position for Supreme Judge Dredd (Elevated Center Throne) */
.stage-overlay-balloon.balloon-dredd {
    top: 3%;
    left: 50%;
    transform: translateX(-50%);
    width: 52%;
    max-width: 520px;
    border: 3.5px solid #F59E0B;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8), 0 0 24px rgba(245, 158, 11, 0.4);
    background: #FFFFFF;
}

.stage-tail-dredd {
    position: absolute;
    bottom: -16px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
    border-top: 16px solid #F59E0B;
}

.stage-tail-dredd-inner {
    position: absolute;
    bottom: -11px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 7px solid transparent;
    border-right: 7px solid transparent;
    border-top: 12px solid #FFFFFF;
}

/* Thinking Balloon State */
.stage-balloon-thinking {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 8px 12px;
    text-align: center;
}

.thinking-dots-row {
    display: flex;
    gap: 6px;
    align-items: center;
    justify-content: center;
    margin-bottom: 6px;
}

.thinking-dots-row span {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #3B82F6;
    animation: pulseDot 1.4s infinite ease-in-out both;
}

.thinking-dots-row span:nth-child(1) { animation-delay: -0.32s; }
.thinking-dots-row span:nth-child(2) { animation-delay: -0.16s; }

/* Live Stage Broadcast Ticker Badge */
.stage-live-ticker {
    position: absolute;
    bottom: 12px;
    left: 14px;
    background: rgba(15, 23, 42, 0.88);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-left: 4px solid #EF4444;
    color: #F8FAFC;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 0.84rem;
    display: flex;
    align-items: center;
    gap: 8px;
    z-index: 15;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6);
}

.live-dot {
    width: 8px;
    height: 8px;
    background-color: #EF4444;
    border-radius: 50%;
    display: inline-block;
    animation: livePulse 1.2s infinite;
}

@keyframes livePulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
    70% { transform: scale(1.15); box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* Content Inside Stage Speech Balloon */
.stage-balloon-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
    padding-bottom: 4px;
    border-bottom: 1.5px solid rgba(15, 23, 42, 0.1);
}

.stage-speaker-tag {
    font-size: 0.88rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    display: flex;
    align-items: center;
    gap: 5px;
}

.stage-model-pill {
    font-size: 0.72rem;
    font-weight: 600;
    color: #475569;
    background: #F1F5F9;
    padding: 1px 6px;
    border-radius: 6px;
}

.stage-round-badge {
    font-size: 0.75rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 6px;
    background: #DCFCE7;
    color: #15803D;
}

.stage-balloon-body {
    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1.42;
    color: #0F172A;
    margin-bottom: 4px;
    letter-spacing: -0.01em;
}

.stage-balloon-chips {
    display: flex;
    gap: 6px;
    margin-top: 5px;
    flex-wrap: wrap;
}

.stage-chip-critique {
    font-size: 0.72rem;
    font-weight: 700;
    color: #DC2626;
    background: #FEE2E2;
    padding: 1px 6px;
    border-radius: 4px;
}

.stage-chip-consensus {
    font-size: 0.72rem;
    font-weight: 700;
    color: #15803D;
    background: #DCFCE7;
    padding: 1px 6px;
    border-radius: 4px;
}

/* Debater Info Bar Under Stage */
.stage-debaters-roster {
    display: flex;
    justify-content: space-around;
    gap: 10px;
    margin-top: -0.5rem;
    margin-bottom: 1.5rem;
}

.roster-card {
    flex: 1;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 8px 12px;
    text-align: center;
    transition: all 0.2s ease;
}

.roster-card.active-speaker {
    background: rgba(30, 41, 59, 0.95);
    transform: translateY(-2px);
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
}

.roster-name {
    font-size: 0.88rem;
    font-weight: 800;
    text-transform: uppercase;
}

.roster-model {
    font-size: 0.72rem;
    color: #94A3B8;
}

/* Pulsing Thinking Animation */
.pulsing-dots {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 5px;
    padding: 6px 0;
}

.pulsing-dots .dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: #60A5FA;
    animation: pulseDot 1.4s infinite ease-in-out both;
}

.pulsing-dots .dot:nth-child(1) { animation-delay: -0.32s; }
.pulsing-dots .dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes pulseDot {
    0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
}

/* Final Verdict Card */
.verdict-card {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%);
    border: 2px solid #10B981;
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 12px 36px rgba(16, 185, 129, 0.2);
}

.verdict-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #34D399;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Model Status Indicators */
.model-status-card {
    padding: 0.55rem 0.8rem;
    border-radius: 8px;
    font-size: 0.82rem;
    line-height: 1.35;
    margin-top: -0.3rem;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

.model-status-card.status-missing-key {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #FCA5A5;
    opacity: 0.85;
}

.model-status-card.status-active-api {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #6EE7B7;
}

.model-status-card.status-local-running {
    background: rgba(6, 182, 212, 0.12);
    border: 1px solid rgba(6, 182, 212, 0.35);
    color: #67E8F9;
}

.model-status-card.status-local-offline {
    background: rgba(148, 163, 184, 0.1);
    border: 1px solid rgba(148, 163, 184, 0.25);
    color: #94A3B8;
}

.model-status-card.status-simulation {
    background: rgba(168, 85, 247, 0.12);
    border: 1px solid rgba(168, 85, 247, 0.3);
    color: #D8B4FE;
}

.provider-pill {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 8px;
    border-radius: 6px;
    font-size: 0.76rem;
    font-weight: 500;
    margin: 2px 3px 2px 0;
}

.provider-pill.active {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.3);
}

.provider-pill.inactive {
    background: rgba(100, 116, 139, 0.15);
    color: #94A3B8;
    border: 1px solid rgba(148, 163, 184, 0.2);
}
</style>
"""
