● Creating Sprites for Arcade Games
  Sprite Sheet Basics

  Sprite sheets are single images containing multiple frames of animation arranged in a grid. They're efficient for
  arcade games because:
  - Single file reduces loading overhead
  - Hardware can quickly switch between frames
  - Easier to manage than separate image files

  Grid Layout

  Organize frames in rows and columns:
  [Frame1] [Frame2] [Frame3] [Frame4]
  [Frame5] [Frame6] [Frame7] [Frame8]
  [Frame9] [Frame10][Frame11][Frame12]

  Common layouts:
  - 4x3 grid = 12 frames (typical for simple animations)
  - 8x4 grid = 32 frames (complex animations)
  - Single row = n frames (simple loops)

  Design Process

  1. Define Animation States

  Plan what animations you need:
  - Idle/standing
  - Walk cycle (usually 4-8 frames)
  - Run cycle (6-12 frames)
  - Jump (3-6 frames: crouch, launch, air, land)
  - Special actions

  2. Frame Dimensions

  - Keep all frames exactly the same size
  - Common sizes: 32x32, 64x64, 128x128 pixels
  - Nextion displays have limited resolution, so optimize accordingly
  - Leave padding if character size varies (centering)

  3. Animation Principles

  Walk Cycle (minimum 4 frames):
  Frame 1: Contact (foot forward)
  Frame 2: Down (lowest point)
  Frame 3: Passing (legs cross)
  Frame 4: Up (highest point)

  Jump (typical 5 frames):
  Frame 1: Crouch/anticipation
  Frame 2: Launch
  Frame 3: Peak (arms/legs extended)
  Frame 4: Descending
  Frame 5: Landing

  4. Pixel Art Tips

  - Consistent pixel density - Keep detail level uniform
  - Limited color palette - Use 8-16 colors for retro style
  - Anti-aliasing - Minimal or none for crispy pixels
  - Outline - 1-2px dark border helps sprites pop from background
  - Squash and stretch - Exaggerate for arcade feel

  Tools

  Free Options:
  - Aseprite (open source) - Best for pixel art sprites
  - GIMP - General purpose, grid tools
  - Piskel - Browser-based pixel editor
  - LibreSprite - Free Aseprite fork

  Commercial:
  - Aseprite (Steam version, ~$20)
  - Photoshop - Industry standard
  - GraphicsGale - Sprite-focused

  For Your Capybara Game

  Looking at your existing sprites in concept/, you can test them:

  # Preview walk animation
  python src/scripts/asset-viewer.py concept/capybara-sprite-walk.png --cols 4 --rows 3 --fps 8

  # Preview run animation (faster playback)
  python src/scripts/asset-viewer.py concept/capybara-sprite-run.png --cols 4 --rows 3 --fps 12

  # Preview jump animation
  python src/scripts/asset-viewer.py concept/capybara-sprite-jump.png --cols 4 --rows 3 --fps 10

  Export for Nextion

  1. Format: PNG or JPG (Nextion supports both)
  2. Size: Calculate total: frame_width × cols, frame_height × rows
  3. Color depth: 16-bit (65K colors) for Nextion displays
  4. Compression: Nextion handles this during compilation

  Animation Timing

  Frame rate guidelines:
  - Idle: 2-4 FPS (slow, subtle)
  - Walk: 8-10 FPS (moderate)
  - Run: 12-15 FPS (fast)
  - Jump: 10-12 FPS (smooth arc)
  - Impact/Hit: 15-20 FPS (quick, punchy)