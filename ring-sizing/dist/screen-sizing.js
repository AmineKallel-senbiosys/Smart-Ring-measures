// Diameter values transcribed from the size guide displayed by the reference.
export const SIZE_CHART=[{size:6,diameter:16.5},{size:7,diameter:17.3},{size:8,diameter:18.1},{size:9,diameter:18.9},{size:10,diameter:19.7},{size:11,diameter:20.5},{size:12,diameter:21.3},{size:13,diameter:22.1},{size:14,diameter:22.8}];
export const CARD_HEIGHT_MM=53.98;
export function pixelsPerMm(cardHeightPixels){if(!Number.isFinite(cardHeightPixels)||cardHeightPixels<80||cardHeightPixels>600)throw new RangeError('Invalid card calibration.');return cardHeightPixels/CARD_HEIGHT_MM;}
export function ringPixels(size,scale){const row=SIZE_CHART.find(r=>r.size===size);if(!row||!Number.isFinite(scale)||scale<=0)throw new RangeError('Invalid ring sizing.');return row.diameter*scale;}
