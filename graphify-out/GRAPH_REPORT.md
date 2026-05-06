# Graph Report - TalentLink  (2026-05-01)

## Corpus Check
- 58 files · ~160,524 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 859 nodes · 1916 edges · 26 communities detected
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 323 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]

## God Nodes (most connected - your core abstractions)
1. `User` - 45 edges
2. `p()` - 36 edges
3. `_call_gemini()` - 29 edges
4. `_()` - 27 edges
5. `nn()` - 26 edges
6. `R()` - 25 edges
7. `e()` - 24 edges
8. `le()` - 24 edges
9. `sn()` - 23 edges
10. `UserData` - 22 edges

## Surprising Connections (you probably didn't know these)
- `User` --calls--> `test_recruiter_registration_flow()`  [INFERRED]
  app\models.py → tests\test_recruiter_flow.py
- `JobPosting` --uses--> `Adds a job posting to the vector database.`  [INFERRED]
  app\models.py → app\utils\vector_utils.py
- `JobPosting` --uses--> `Adds a user's resume summary to the vector database.`  [INFERRED]
  app\models.py → app\utils\vector_utils.py
- `JobPosting` --uses--> `Semantically searches for jobs matching the resume text.     Returns a list of`  [INFERRED]
  app\models.py → app\utils\vector_utils.py
- `JobPosting` --uses--> `Semantically searches for resumes matching a job description.     Returns a lis`  [INFERRED]
  app\models.py → app\utils\vector_utils.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.03
Nodes (106): approve_recruiter(), reject_recruiter(), AIAgent, CareerForecast, JobPosting, Notification, Organization, Quest (+98 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (98): generate_job_desc_api(), market_intelligence(), EmotionalState, ExternalApplication, GitHubProfile, MockTest, FlaskForm, api_chatbot() (+90 more)

### Community 2 - "Community 2"
Cohesion: 0.02
Nodes (14): Bg(), bu(), Cf(), en(), Hh(), hn(), jr(), Kh() (+6 more)

### Community 3 - "Community 3"
Cohesion: 0.07
Nodes (83): a(), ag(), am(), Av(), Bi(), bn(), bv(), C() (+75 more)

### Community 4 - "Community 4"
Cohesion: 0.05
Nodes (80): _(), af(), an(), ao(), b(), bo(), Cg(), cn() (+72 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (30): JobPostingForm, create_job(), create_quest(), dashboard(), edit_job(), interview_funnel(), reindex_vectors(), send_user_notification() (+22 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (26): JobApplication, MockInterview, UserData, CareerForecastService, Generates a career forecast including a future resume and gap analysis., InterviewService, Fetches relevant context (skills, field) for the user., Generates the next interview question with adaptive difficulty, type, and agent (+18 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (24): aa(), ae(), be(), ca(), fa(), fe(), ga(), Ge() (+16 more)

### Community 8 - "Community 8"
Cohesion: 0.18
Nodes (17): ba(), ce(), Ee(), he(), ie(), je(), ke(), Me() (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.18
Nodes (15): ai(), ei(), Gr(), hr(), ii(), l(), Nf(), ni() (+7 more)

### Community 10 - "Community 10"
Cohesion: 0.16
Nodes (8): Config, DevelopmentConfig, ProductionConfig, TestingConfig, create_app(), app(), client(), test_recruiter_registration_flow()

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (12): view_analysis(), resume_analysis_result(), fetch_yt_video_title(), get_curated_courses(), get_dynamic_bonus_videos(), get_random_bonus_videos(), load_config(), Returns curated course recommendations based on the predicted field. (+4 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (12): as(), is(), ja(), ls(), ns(), oi(), si(), ta() (+4 more)

### Community 13 - "Community 13"
Cohesion: 0.21
Nodes (12): de(), ea(), gi(), ji(), jo(), ki(), la(), qi() (+4 more)

### Community 14 - "Community 14"
Cohesion: 0.25
Nodes (1): NeuralNetworkBackground

### Community 15 - "Community 15"
Cohesion: 0.27
Nodes (1): TelemetryEngine

### Community 16 - "Community 16"
Cohesion: 0.32
Nodes (2): animateParticles(), Particle

### Community 17 - "Community 17"
Cohesion: 0.29
Nodes (2): handle_end_interview(), Finalizes the interview using the service.

### Community 18 - "Community 18"
Cohesion: 0.4
Nodes (1): SentientLog

### Community 19 - "Community 19"
Cohesion: 0.33
Nodes (6): di(), fi(), go(), hi(), li(), pi()

### Community 22 - "Community 22"
Cohesion: 0.67
Nodes (2): animate(), getScreenCoordinates()

### Community 23 - "Community 23"
Cohesion: 0.5
Nodes (4): Bt(), ft(), lt(), pt()

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (3): Gm(), lm(), Wm()

### Community 26 - "Community 26"
Cohesion: 0.67
Nodes (3): bf(), of(), Pf()

### Community 27 - "Community 27"
Cohesion: 0.67
Nodes (3): lf(), rf(), uf()

### Community 28 - "Community 28"
Cohesion: 0.67
Nodes (3): ed(), td(), Vp()

## Knowledge Gaps
- **41 isolated node(s):** `Society`, `AIAgent`, `Stores the AI-generated 'Future Resume' and career trajectory.`, `Finalizes the interview using the service.`, `Cleans a string to extract valid JSON content, removing markdown blocks and whit` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 14`** (11 nodes): `scene.js`, `NeuralNetworkBackground`, `.addEventListeners()`, `.animate()`, `.constructor()`, `.handleCardTilt()`, `.initLights()`, `.initNetwork()`, `.onMouseMove()`, `.onResize()`, `.resetCardTilt()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (10 nodes): `telemetry.js`, `TelemetryEngine`, `.analyzeState()`, `.constructor()`, `.flashMessage()`, `.init()`, `.trackClick()`, `.trackMouse()`, `.trackTyping()`, `.triggerReaction()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (8 nodes): `landing_animations.js`, `animateParticles()`, `initParticles()`, `Particle`, `.constructor()`, `.draw()`, `.update()`, `resize()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (7 nodes): `handle_connect()`, `handle_disconnect()`, `handle_end_interview()`, `handle_send_answer()`, `handle_start_interview()`, `socket_events.py`, `Finalizes the interview using the service.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (6 nodes): `main.js`, `SentientLog`, `.addLog()`, `.constructor()`, `.init()`, `updateThemeIcon()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (4 nodes): `sphere_effect.js`, `animate()`, `generateFibonacciSphere()`, `getScreenCoordinates()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `Community 0` to `Community 10`, `Community 5`, `Community 6`?**
  _High betweenness centrality (0.055) - this node is a cross-community bridge._
- **Why does `UserData` connect `Community 6` to `Community 0`, `Community 1`, `Community 5`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `JobPosting` connect `Community 0` to `Community 5`, `Community 6`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `User` (e.g. with `PasswordStrength` and `LoginForm`) actually correct?**
  _`User` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `_call_gemini()` (e.g. with `api_chatbot()` and `.generate_forecast()`) actually correct?**
  _`_call_gemini()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Society`, `AIAgent`, `Stores the AI-generated 'Future Resume' and career trajectory.` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.03 - nodes in this community are weakly interconnected._