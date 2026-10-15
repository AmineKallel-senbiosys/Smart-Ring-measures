# Local scan debugging

The running scan server groups each scan attempt into `Test N1`, `Test N2`, and so on. Numbering continues after a server restart. Each numbered folder contains `test-info.json` plus timestamped request folders for its preview frames and captured photo. `input.jpg` or `input.png` is the exact image received by the sizing worker. `report.json` records the request mode, timing, detector checks, measurement details or error. Inspect requests are the live camera frames; analyze requests are the captured photo and final result. Retrying or repeating capture starts a new numbered test.

These files contain private hand photos. This folder is outside the served `ring-sizing/dist` directory and has no public HTTP route. No credentials, cookies or ngrok tokens are logged. Test files remain on this PC until you remove them. Set RING_TEST_CAPTURE=0 before starting the server to stop saving new test files.

Each photo that reaches finger measurement now also saves `measurements.jpg` and `finger-measurements.json`. Green marks the detected card. Blue lines are accepted width samples, red lines are rejected samples with visible edges, and pink is the chosen median-width line. The JSON contains pixel coordinates, rejected section reasons, widths in pixels and mm, consensus/MAD checks, card scale, exact circumference formula, quality formula/caps and the product interval used for each finger. Coordinates refer to the worker image dimensions in report.json. A finger without reliable edges records its failure reason and no invented size. Failures before finger measurement (e.g. a black photo or missing card) have no measurement overlay.

Do one complete test, then tell me which finger results were wrong and your actual measured circumference if known. I can inspect the latest session here.

## Diagnosis of the two 2026-10-14 captures

Session c30d7d0b-0948-42a7-a3b9-e07993d3a936: both analyze images (14:33:53Z and 14:34:06Z) contain exclusively RGB zero pixels, mean 0 and maximum 0. Both are 1327 x 2400 JPEGs of 51,465 bytes. Immediately preceding preview frames detect hand, card, separated fingers, flatness and framing successfully. This isolates the failure to the final snapshot path, not a missing hand in the scene.

The capture path now keeps a materialized canvas snapshot instead of creating an ImageBitmap from that canvas, verifies pixel content while the camera is live, and copies the pixels back before stopping the stream. A black still falls back to the live video capture. If both sources are black, capture stays open and shows a camera error instead of submitting the blank photo for hand detection. Actual phone verification remains necessary.
