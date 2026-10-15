# AI Hand Scan

Only the hand-scan flow is active. The PC displays a session QR, the phone captures a hand and a standard card, and automatic results appear on both devices. Continue on this device also supports PC capture. Available products remain US 6, 8, 10 and 12, with the exact supplied circumference/fit intervals in product-fit.json.

## Run and check

Run npm start from this directory (Node 24). The server listens on port 4173 behind the existing ngrok tunnel. The native worker uses Python 3.11 and .vision-tools (MediaPipe, OpenCV and NumPy). The local model is dist/vision/hand_landmarker.task. Set RING_PYTHON when using a different interpreter.

Run npm test and python -m unittest test_hand_segmentation.py test_measurement_geometry.py test_fit_rules.py test_calibration_model.py. Geometry tests use known pixel silhouettes and synthetic hands, not real-world sizing ground truth. node verify-live.mjs checks rejection of the private low-resolution recording and synchronization of synthetic API measurements, then clears them. It does not demonstrate physical accuracy.

## Measurement pipeline v3

1. MediaPipe identifies the hand and finger landmarks.
   Missed detections retry at a smaller inference scale, three rotations and local contrast normalization. Rotated/scaled landmarks are mapped back to the original measurement pixels. Detection/presence thresholds are 0.35/0.4; card and actual edge requirements still apply.
   Capture prefers a camera still through ImageCapture where the browser/device supports it, then falls back to a video snapshot. Original photo upload remains available. Uploaded images retain up to 2400 pixels on their long side; the display canvas size does not affect the metric calculation.
2. OpenCV finds the full outer contour of an 85.60 x 53.98 mm card. A fitted rectangle avoids shrinking its rounded corners during polygon simplification. Angled or undersized references are rejected.
3. A pretrained MobileSAM encoder and mask decoder segment the hand locally using landmark prompts. ONNX Runtime runs on the PC CPU. Landmark-guided GrabCut is a fallback when the learned mask fails its coverage checks; its candidate region now includes the full landmark hull instead of locking real finger edges outside narrow tubes as background.
4. Forty perpendicular cross sections are examined around the proximal ring-wearing position. Additional sections near the joint can recover partly webbed fingers, with quality capped at 70%. Mask boundaries constrain the search, and a bidirectional colour derivative plus parabolic peak refinement locates edges between pixels. A robust median rejects outliers. At least eight agreeing sections are required. Contour-only fallback is capped at 55% and GrabCut at 65%.
5. The active flow skips visual alignment and returns results automatically. A failed finger is explicitly unmeasured, with no circumference, diameter or product size and 0% automatic quality; valid fingers retain their measurements. Landmark-width proposals are never converted into sizes.
6. A validated local calibration can map measured width to circumference. Without calibration, C = width x pi retains the supplied camera scanner's circular-width estimate. It is explicitly not a measurement of finger depth or a validated fit prediction.
7. The server applies product-fit.json to full-precision circumferences and immediately synchronizes the automatic results to phone and PC. Percentages remain image measurement quality, not probability of fit. No manual alignment or confirmation is required.

The other supplied camera project at ../../AI RING SIZE/src/components/camera/CameraScan.tsx also supports visual alignment and computes C from a card-calibrated width. The active hand scan uses automatic measurements and does not load the optional alignment module.

## Accuracy and calibration

The runtime checks each photo at its original processing scale and at 85% scale when both meet the resolution minimum. Different product sizes, circumference differences over 0.75 mm or comparison failure mark a finger unstable, cap its image-quality score at 50% and show a retry notice. This checks processing sensitivity only, not physical accuracy. The full-resolution estimate remains the reported estimate. The private three-test benchmark in ../test/accuracy-review.md still matches only 5/12 supplied product labels; this implementation is not yet a validated sizing system. benchmark_scans.py replays those development photos, with labels excluded from prediction logic.

The previous threshold-based edge scanner and a guessed 0.85 ellipse ratio have been superseded. Better edge precision does not establish true circumference: a top-down image cannot directly observe finger depth, knuckle passage, tissue compression or desired fit. The user's known sizes (little 8, ring 8, middle 10, index 10) are validation targets, never forced outputs.

No calibration model ships enabled. To train one, populate calibration-pairs.template.csv with stable anonymous person codes, finger identifiers, widths from this v3 photo pipeline and independently measured circumferences in mm. A known US size is not an exact circumference and is insufficient as a training label. At least 30 real pairs across five people are required. Different captures of the same person must use the same person code.

Run python calibration_model.py calibration-pairs.csv --output measurement-calibration.json. The tool evaluates predictions with each person excluded from training. It refuses a model whose held-person-out MAE exceeds 0.75 mm or maximum error exceeds 2 mm, and saves coefficients, validation metrics, observed width bounds and pipeline identity. Those thresholds are an engineering acceptance check, not a claim of guaranteed product fit. Keep a separate real-use validation set as well. The runtime refuses incompatible/unvalidated files and applies a valid model only within the observed width range. Outside it, estimates remain uncalibrated. No coefficients from another study or arbitrary depth factor are copied.

A measured-circumference correction is still available on results. This updates the product size and zone on both devices while preserving original photo measurements and quality. It is marked as measured rather than inferred.

## Camera guide and model setup

The full-screen camera follows the second recording: upper-left hand/card reference, card/hand divider, moving level bubble with real degrees, three placement checks and a three-second steady countdown. On iOS, Start requests motion access from the user gesture. Missing sensor access displays an unavailable angle rather than a fabricated zero. Tilt or failed placement cancels automatic capture. Preview checks and captured stills use the same visible cover crop.

The native dependencies also require ONNX Runtime. The two MobileSAM ONNX weights live in models, outside dist. Run python download_segmentation_models.py to restore the pinned public exports; model-manifest.json records their source revision and SHA-256 hashes. See models/NOTICE.md and MobileSAM-LICENSE.txt for licensing. Downloading weights never uploads a hand photo.

The private recording diagnostic recovered three fingers in record.mp4 and four in record 2.mp4. Both recordings are below the production minimum of 3 pixels/mm and cannot validate circumference accuracy. The first recording's little finger remains unavailable. check_recording_measurements.py deliberately checks edge availability only, without upscaling recordings to pass the resolution gate. Tests include test_neural_hand_mask.py in addition to the suites above.

## Photo handling

Update: the user explicitly requested local test recording. `../test/Test N<number>/<request>/` now retains each received preview frame or captured photo plus `report.json` with dimensions, processing duration, checks, errors and detailed results. Each capture attempt groups its preview and photo requests in one numbered folder, and numbering continues after restarting the server. These files are outside the public web root and excluded from Git. They are retained until manually removed; set RING_TEST_CAPTURE=0 before server startup to restore memory-only photo handling. The following paragraph describes that memory-only mode.

Photo analyses that reach finger measurement also save `measurements.jpg` and `finger-measurements.json`: card calibration, landmark coordinates, every attempted cross section and rejection reason, pixel/mm widths, consensus median/MAD, exact circumference formula, quality caps and the selected product rule. Blue overlay lines are accepted samples, red are rejected samples with detected edges, pink is the median-width line, and green is the card. The trace records current estimates; it does not improve or validate accuracy by itself. Run test_measurement_trace.py to check trace/geometry consistency and annotated-image generation.

The user approved phone-to-PC photos/camera frames through ngrok. No external AI service receives them. The worker processes images in memory and releases each input; the server never writes an upload to disk. The captured bitmap is closed after automatic analysis or page exit. Only measurements live in paired server sessions for up to two hours. Reloading requires another capture because the photo is not retained by the server. Private extracted recording frames remain outside dist. Calibration CSVs/models are outside the served web root and excluded from Git.

## Product rules

US 6 owns [50.6,54.45), with OK [51.25,51.9]. US 8 owns [54.45,59.55), with OK [55.725,57]. US 10 owns [59.55,64.65), with OK [60.825,62.1]. US 12 owns [64.65,infinity), with OK [65.925,67.2]. Below each OK interval is Loose; above it is Tight. Below 50.6 mm there is no matching product. The US 12 Tight zone has no upper cutoff, as supplied. Display rounding does not change classification.

## Sources and limits

Aitaca publicly describes guided hand photos, computer vision and product-specific sizing, but those descriptions do not supply its trained sizing model or an integration contract. No Circular/Aitaca account session, key or external image endpoint is reused. Genuine Aitaca operation requires an authorized integration.

Independent architecture references:
- https://github.com/ChaoningZhang/MobileSAM
- https://huggingface.co/Acly/MobileSAM
- https://www.w3.org/TR/orientation-event/
- https://docs.opencv.org/4.x/d8/d83/tutorial_py_grabcut.html
- https://fengx.io/work/ring-sizer-sub-millimeter-finger-measurement-via-computer-vision/
- https://www.aitaca.io/solutions/jewelry/

The case study supports segmentation, multiple sections, subpixel localization and held-person-out calibration as an engineering approach; its coefficients and reported accuracy do not validate this project. This independent implementation still needs original hand-and-card photos paired with real circumference measurements to establish sizing accuracy.
