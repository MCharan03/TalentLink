# Graph Report - TalentLink  (2026-05-07)

## Corpus Check
- 114 files · ~183,615 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1225 nodes · 2332 edges · 42 communities detected
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 349 edges (avg confidence: 0.66)
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
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]

## God Nodes (most connected - your core abstractions)
1. `User` - 45 edges
2. `p()` - 36 edges
3. `_call_gemini()` - 31 edges
4. `_()` - 27 edges
5. `nn()` - 26 edges
6. `R()` - 25 edges
7. `e()` - 25 edges
8. `le()` - 24 edges
9. `sn()` - 23 edges
10. `UserData` - 22 edges

## Surprising Connections (you probably didn't know these)
- `test_recruiter_registration_flow()` --calls--> `User`  [INFERRED]
  web\backend\tests\test_recruiter_flow.py → web\backend\models.py
- `Adds a job posting to the vector database.` --uses--> `JobPosting`  [INFERRED]
  app\utils\vector_utils.py → web\backend\models.py
- `Adds a user's resume summary to the vector database.` --uses--> `JobPosting`  [INFERRED]
  app\utils\vector_utils.py → web\backend\models.py
- `Semantically searches for jobs matching the resume text.     Returns a list of` --uses--> `JobPosting`  [INFERRED]
  app\utils\vector_utils.py → web\backend\models.py
- `Semantically searches for resumes matching a job description.     Returns a lis` --uses--> `JobPosting`  [INFERRED]
  app\utils\vector_utils.py → web\backend\models.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.01
Nodes (192): ats_simulator_view.dart, AuthWrapper, _AuthWrapperState, build, initState, LoginView, main, MainNavigation (+184 more)

### Community 1 - "Community 1"
Cohesion: 0.03
Nodes (107): approve_recruiter(), reject_recruiter(), ForgotPasswordForm, LoginForm, PasswordStrength, Custom validator for password strength., RecruiterRegistrationForm, RegistrationForm (+99 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (97): generate_job_desc_api(), market_intelligence(), ExternalApplication, MockTest, FlaskForm, CareerForecastService, ChangePasswordForm, LinkedInBuilderForm (+89 more)

### Community 3 - "Community 3"
Cohesion: 0.02
Nodes (24): Bg(), Bi(), Cx(), dm(), ed(), Hh(), hn(), Hp() (+16 more)

### Community 4 - "Community 4"
Cohesion: 0.08
Nodes (71): a(), ag(), am(), Av(), bv(), C(), Cg(), cv() (+63 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (31): apply_job(), mobile_dashboard(), mobile_interview_message(), start_mobile_interview(), JobApplication, MockInterview, UserData, Exception (+23 more)

### Community 6 - "Community 6"
Cohesion: 0.05
Nodes (30): JobPostingForm, create_job(), create_quest(), dashboard(), edit_job(), interview_funnel(), reindex_vectors(), send_user_notification() (+22 more)

### Community 7 - "Community 7"
Cohesion: 0.09
Nodes (35): af(), ch(), cn(), f(), Gm(), Gr(), gu(), hr() (+27 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (34): _(), ba(), bf(), bu(), ce(), Cf(), Df(), Ee() (+26 more)

### Community 9 - "Community 9"
Cohesion: 0.09
Nodes (30): ao(), b(), bo(), Bt(), Co(), cr(), d(), Do() (+22 more)

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (19): RegisterPlugins(), FlutterWindow(), OnCreate(), Create(), Destroy(), EnableFullDpiSupportIfAvailable(), GetClientArea(), GetThisFromHandle() (+11 more)

### Community 11 - "Community 11"
Cohesion: 0.11
Nodes (25): aa(), ae(), be(), ca(), de(), ea(), fe(), ga() (+17 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (23): an(), dn(), fn(), ho(), In(), l(), m(), Nf() (+15 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (19): ai(), bn(), ei(), gi(), hi(), ii(), ji(), jo() (+11 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (19): as(), di(), fa(), fi(), go(), is(), ja(), li() (+11 more)

### Community 15 - "Community 15"
Cohesion: 0.16
Nodes (8): Config, DevelopmentConfig, ProductionConfig, TestingConfig, create_app(), app(), client(), test_recruiter_registration_flow()

### Community 16 - "Community 16"
Cohesion: 0.14
Nodes (4): fl_register_plugins(), main(), my_application_activate(), my_application_new()

### Community 17 - "Community 17"
Cohesion: 0.22
Nodes (12): view_analysis(), resume_analysis_result(), fetch_yt_video_title(), get_curated_courses(), get_dynamic_bonus_videos(), get_random_bonus_videos(), load_config(), Returns curated course recommendations based on the predicted field. (+4 more)

### Community 18 - "Community 18"
Cohesion: 0.2
Nodes (5): EmotionalState, SkillFitAssessment, SkillFitService, api_telemetry(), seed_skillfit()

### Community 19 - "Community 19"
Cohesion: 0.25
Nodes (1): NeuralNetworkBackground

### Community 20 - "Community 20"
Cohesion: 0.2
Nodes (2): handle_end_interview(), Finalizes the interview using the service.

### Community 21 - "Community 21"
Cohesion: 0.27
Nodes (1): TelemetryEngine

### Community 22 - "Community 22"
Cohesion: 0.22
Nodes (3): FlutterAppDelegate, FlutterImplicitEngineDelegate, AppDelegate

### Community 23 - "Community 23"
Cohesion: 0.22
Nodes (8): dispose, _initCamera, MultimodalService, dart:io, package:camera/camera.dart, package:flutter/foundation.dart, package:permission_handler/permission_handler.dart, package:speech_to_text/speech_to_text.dart

### Community 24 - "Community 24"
Cohesion: 0.32
Nodes (2): animateParticles(), Particle

### Community 25 - "Community 25"
Cohesion: 0.29
Nodes (6): Analysis, Application, DashboardData, ExternalApp, Quest, UserInfo

### Community 26 - "Community 26"
Cohesion: 0.29
Nodes (6): AuraColors, AuraTheme, BoxDecoration, glassDecoration, ThemeData, package:google_fonts/google_fonts.dart

### Community 27 - "Community 27"
Cohesion: 0.29
Nodes (4): Text, update_schema(), add_column_if_not_exists(), update_schema()

### Community 28 - "Community 28"
Cohesion: 0.33
Nodes (3): RegisterGeneratedPlugins(), NSWindow, MainFlutterWindow

### Community 29 - "Community 29"
Cohesion: 0.47
Nodes (4): wWinMain(), CreateAndAttachConsole(), GetCommandLineArguments(), Utf8FromUtf16()

### Community 31 - "Community 31"
Cohesion: 0.4
Nodes (1): SentientLog

### Community 32 - "Community 32"
Cohesion: 0.4
Nodes (2): RunnerTests, XCTestCase

### Community 33 - "Community 33"
Cohesion: 0.5
Nodes (2): handle_new_rx_page(), Intercept NOTIFY_DEBUGGER_ABOUT_RX_PAGES and touch the pages.

### Community 36 - "Community 36"
Cohesion: 0.67
Nodes (2): animate(), getScreenCoordinates()

### Community 37 - "Community 37"
Cohesion: 0.67
Nodes (2): GeneratedPluginRegistrant, -registerWithRegistry

### Community 38 - "Community 38"
Cohesion: 0.67
Nodes (2): FlutterSceneDelegate, SceneDelegate

### Community 39 - "Community 39"
Cohesion: 0.67
Nodes (2): SkillNode, SkillTreeData

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): MainActivity

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): AtsAnalysis

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): JobPosting

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Stores the AI-generated 'Future Resume' and career trajectory.

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Finalizes the interview using the service.

## Knowledge Gaps
- **249 isolated node(s):** `MainActivity`, `Intercept NOTIFY_DEBUGGER_ABOUT_RX_PAGES and touch the pages.`, `-registerWithRegistry`, `TalentLinkApp`, `AuthWrapper` (+244 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 19`** (11 nodes): `NeuralNetworkBackground`, `.addEventListeners()`, `.animate()`, `.constructor()`, `.handleCardTilt()`, `.initLights()`, `.initNetwork()`, `.onMouseMove()`, `.onResize()`, `.resetCardTilt()`, `scene.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (10 nodes): `handle_connect()`, `handle_disconnect()`, `handle_end_interview()`, `handle_media_chunk()`, `handle_send_answer()`, `handle_skillfit_end()`, `handle_skillfit_start()`, `handle_start_interview()`, `Finalizes the interview using the service.`, `socket_events.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (10 nodes): `TelemetryEngine`, `.analyzeState()`, `.constructor()`, `.flashMessage()`, `.init()`, `.trackClick()`, `.trackMouse()`, `.trackTyping()`, `.triggerReaction()`, `telemetry.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (8 nodes): `animateParticles()`, `initParticles()`, `Particle`, `.constructor()`, `.draw()`, `.update()`, `resize()`, `landing_animations.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (6 nodes): `SentientLog`, `.addLog()`, `.constructor()`, `.init()`, `updateThemeIcon()`, `main.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (5 nodes): `RunnerTests.swift`, `RunnerTests.swift`, `RunnerTests`, `.testExample()`, `XCTestCase`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (4 nodes): `handle_new_rx_page()`, `__lldb_init_module()`, `Intercept NOTIFY_DEBUGGER_ABOUT_RX_PAGES and touch the pages.`, `flutter_lldb_helper.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (4 nodes): `animate()`, `generateFibonacciSphere()`, `getScreenCoordinates()`, `sphere_effect.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (3 nodes): `GeneratedPluginRegistrant.m`, `GeneratedPluginRegistrant`, `-registerWithRegistry`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (3 nodes): `FlutterSceneDelegate`, `SceneDelegate.swift`, `SceneDelegate`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (3 nodes): `SkillNode`, `SkillTreeData`, `skill_tree_data.dart`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (2 nodes): `MainActivity.kt`, `MainActivity`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (2 nodes): `AtsAnalysis`, `ats_analysis.dart`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (2 nodes): `JobPosting`, `job_data.dart`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Stores the AI-generated 'Future Resume' and career trajectory.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Finalizes the interview using the service.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SystemSetting` connect `Community 1` to `Community 27`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `Text` connect `Community 27` to `Community 0`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Why does `update_schema()` connect `Community 27` to `Community 1`?**
  _High betweenness centrality (0.105) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `User` (e.g. with `PasswordStrength` and `LoginForm`) actually correct?**
  _`User` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `_call_gemini()` (e.g. with `start_mobile_interview()` and `mobile_interview_message()`) actually correct?**
  _`_call_gemini()` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `MainActivity`, `Intercept NOTIFY_DEBUGGER_ABOUT_RX_PAGES and touch the pages.`, `-registerWithRegistry` to the rest of the system?**
  _249 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.01 - nodes in this community are weakly interconnected._