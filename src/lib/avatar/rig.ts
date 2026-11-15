// Copyright (c) 2026 Belikhun. Licensed under the MIT License.
// See LICENSE at the repository root.

// A small Live2D-style rig. The avatar is a stack of layers cut from one
// illustration (scripts/avatar.py); each layer is a grid mesh over one shared
// texture, and every frame the grid is bent by a handful of parameters: the
// head's angle, the breath, the blink, and two springs for hair and skirt.
//
// All coordinates are in the model's own pixels, a 1280 by 1280 frame.

/** One layer as scripts/avatar.py placed it. */
export interface LayerData {
	name: string;
	x: number;
	y: number;
	width: number;
	height: number;
	u: number;
	v: number;
}

/** The manifest written beside the atlas. */
export interface AvatarData {
	size: number[];
	atlas: number[];
	layers: LayerData[];
}

/** What a scene animates. Angles and looks run from -1 to 1, the rest from 0 to 1. */
export interface Pose {
	angleX: number;
	angleY: number;
	lookX: number;
	lookY: number;
	breath: number;
	eyeOpen: number;
	wind: number;
}

/** A running rig. */
export interface Rig {
	pose: Pose;
	render(seconds: number, deltaSeconds: number): void;
	resize(): void;
	destroy(): void;
}

/** The part of the model frame the flat illustration covers. */
export const SOURCE_BOX = { x: 262.5, y: 0, width: 755, height: 1280 };

/** The part of the model frame the canvas shows: the illustration plus room for the hair to swing. */
export const VIEW = { x: 192.5, y: -40, width: 895, height: 1350 };

const CELL = 26;
const MAX_PIXEL_RATIO = 2;

const HEAD = { x: 540, y: 190 };
const NECK = { x: 552, y: 300 };
const SHOULDER_RIGHT = { x: 490, y: 330 };
const SHOULDER_LEFT = { x: 631, y: 330 };
const HIP = { x: 705, y: 655 };
const WAIST = 470;
const HEM = 1073;

/** Each eye closes towards its lower lid. */
const EYES = {
	r: { top: 207, bottom: 250 },
	l: { top: 184, bottom: 229 }
};

/**
 * How far each head layer shifts when the head turns; nearer layers move a
 * little more. The spread is kept narrow: a wide one pulls the face away from
 * the hair around it.
 */
const DEPTH: Record<string, number> = {
	'front hair': 1.25,
	face: 1,
	ears: 0.9,
	nose: 1.2,
	mouth: 1.15,
	'eyebrow-l': 1.15,
	'eyebrow-r': 1.15,
	'eyewhite-l': 1.12,
	'eyewhite-r': 1.12,
	'irides-l': 1.14,
	'irides-r': 1.14,
	'eyelash-l': 1.15,
	'eyelash-r': 1.15
};

const BACK_HAIR_DEPTH = 0.8;
const NECK_DEPTH = 0.9;
const TURN_X = 4;
const TURN_Y = 3;
const TILT = (2 * Math.PI) / 180;
const LEAN = (0.7 * Math.PI) / 180;
const BREATH_LIFT = 3;

const VERTEX_SHADER = `
attribute vec2 position;
attribute vec2 texel;
uniform vec4 view;
varying vec2 uv;

void main() {
	vec2 clip = (position - view.xy) / view.zw * 2.0 - 1.0;
	gl_Position = vec4(clip.x, -clip.y, 0.0, 1.0);
	uv = texel;
}`;

const FRAGMENT_SHADER = `
precision mediump float;
uniform sampler2D atlas;
varying vec2 uv;

void main() {
	gl_FragColor = texture2D(atlas, uv);
}`;

interface Springs {
	hair: number;
	hairSpeed: number;
	skirt: number;
	skirtSpeed: number;
	lastAngleX: number;
}

interface Frame extends Pose {
	time: number;
	hair: number;
	skirt: number;
	tilt: number;
}

interface Point {
	x: number;
	y: number;
}

function smooth(from: number, to: number, value: number): number {
	const amount = Math.min(1, Math.max(0, (value - from) / (to - from)));

	return amount * amount * (3 - 2 * amount);
}

function rotate(point: Point, pivot: Point, radians: number): void {
	const cos = Math.cos(radians);
	const sin = Math.sin(radians);
	const x = point.x - pivot.x;
	const y = point.y - pivot.y;

	point.x = pivot.x + x * cos - y * sin;
	point.y = pivot.y + x * sin + y * cos;
}

/** The whole upper body leans a little with the head, so the head never moves alone. */
function lean(point: Point, frame: Frame, weight: number): void {
	rotate(point, HIP, frame.angleX * LEAN * weight);
}

/** The head's own motion: a tilt about the neck, then a shift that grows with depth. */
function turnHead(point: Point, frame: Frame, depth: number, weight: number): void {
	rotate(point, NECK, frame.tilt * weight);
	point.x += frame.angleX * depth * TURN_X * weight;
	point.y += frame.angleY * depth * TURN_Y * weight - frame.breath * BREATH_LIFT;
}

function bendBackHair(point: Point, frame: Frame): void {
	const distance = Math.hypot(point.x - HEAD.x, point.y - HEAD.y);
	const loose = smooth(120, 640, distance);

	// the roots follow the head; the lengths lag behind and swing
	lean(point, frame, 1);
	turnHead(point, frame, BACK_HAIR_DEPTH, 1 - smooth(110, 420, distance));
	point.x += frame.hair * loose * loose * 70 + Math.sin(frame.time * 1.6 - distance * 0.011) * loose * 7 * frame.wind;
	point.y += Math.cos(frame.time * 1.1 - distance * 0.009) * loose * 3 * frame.wind;
}

function bendFrontHair(point: Point, frame: Frame): void {
	const tip = smooth(150, 320, point.y);

	lean(point, frame, 1);
	turnHead(point, frame, DEPTH['front hair']!, 1);
	point.x += frame.hair * tip * 10 + Math.sin(frame.time * 2.1 - point.y * 0.03) * tip * 1.8 * frame.wind;
}

function bendDress(point: Point, frame: Frame): void {
	const below = smooth(WAIST, HEM, point.y);

	lean(point, frame, 1 - below);
	point.x += (point.x - 560) * frame.breath * 0.012 * (1 - smooth(330, WAIST, point.y) * 0.5) * (1 - below);
	point.y -= frame.breath * BREATH_LIFT * (1 - below);
	point.x += frame.skirt * below * below * 45 + Math.sin(frame.time * 1.4 - point.y * 0.012) * below * 5 * frame.wind;
}

function bendArm(point: Point, frame: Frame, shoulder: Point, side: number): void {
	rotate(point, shoulder, side * (frame.breath * 0.014 + frame.skirt * 0.03));
	lean(point, frame, 1);
	point.y -= frame.breath * BREATH_LIFT;
}

function bendLegs(point: Point, frame: Frame): void {
	rotate(point, HIP, frame.skirt * -0.025 + Math.sin(frame.time * 0.9) * 0.01 * frame.wind);
}

function bendEye(point: Point, frame: Frame, name: string): void {
	const eye = name.endsWith('-r')
		? EYES.r
		: EYES.l;

	if (name.startsWith('eyelash')) {
		point.y += (1 - frame.eyeOpen) * (eye.bottom - eye.top) * 0.62;
	} else {
		point.y = eye.bottom - (eye.bottom - point.y) * frame.eyeOpen;
	}

	if (name.startsWith('irides')) {
		point.x += frame.lookX * 2.2;
		point.y += frame.lookY * 1.6 * frame.eyeOpen;
	}

	lean(point, frame, 1);
	turnHead(point, frame, DEPTH[name]!, 1);
}

/** The top of the neck goes with the head; its base stays in the collar. */
function bendNeck(point: Point, frame: Frame): void {
	lean(point, frame, 1);
	turnHead(point, frame, NECK_DEPTH, 1 - smooth(255, 320, point.y));
}

function bend(name: string, point: Point, frame: Frame): void {
	if (name === 'back hair') {
		bendBackHair(point, frame);
	} else if (name === 'front hair') {
		bendFrontHair(point, frame);
	} else if (name === 'topwear') {
		bendDress(point, frame);
	} else if (name === 'handwear-r') {
		bendArm(point, frame, SHOULDER_RIGHT, 1);
	} else if (name === 'handwear-l') {
		bendArm(point, frame, SHOULDER_LEFT, -1);
	} else if (name === 'legwear' || name === 'footwear') {
		bendLegs(point, frame);
	} else if (name === 'neck') {
		bendNeck(point, frame);
	} else if (name.startsWith('eyewhite') || name.startsWith('irides') || name.startsWith('eyelash')) {
		bendEye(point, frame, name);
	} else {
		lean(point, frame, 1);
		turnHead(point, frame, DEPTH[name] ?? 1, 1);
	}
}

function compile(gl: WebGLRenderingContext, type: number, source: string): WebGLShader {
	const shader = gl.createShader(type)!;

	gl.shaderSource(shader, source);
	gl.compileShader(shader);

	if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
		throw new Error(gl.getShaderInfoLog(shader) ?? 'shader failed to compile');
	}

	return shader;
}

/**
 * Starts a rig on a canvas.
 *
 * @param canvas sized by CSS; the rig keeps its backing store in step
 * @param data the manifest from scripts/avatar.py
 * @param atlas the decoded atlas picture
 * @returns the rig, or `undefined` where WebGL is not available
 */
export function createRig(canvas: HTMLCanvasElement, data: AvatarData, atlas: HTMLImageElement): Rig | undefined {
	const gl = canvas.getContext('webgl', { premultipliedAlpha: true, antialias: true });

	if (!gl) {
		return undefined;
	}

	const base: number[] = [];
	const texels: number[] = [];
	const indices: number[] = [];
	const spans: { name: string; first: number; count: number }[] = [];
	const [atlasWidth, atlasHeight] = data.atlas as [number, number];

	for (const layer of data.layers) {
		const columns = Math.max(1, Math.ceil(layer.width / CELL));
		const rows = Math.max(1, Math.ceil(layer.height / CELL));
		const first = base.length / 2;

		for (let row = 0; row <= rows; row++) {
			for (let column = 0; column <= columns; column++) {
				const across = (column / columns) * layer.width;
				const down = (row / rows) * layer.height;

				base.push(layer.x + across, layer.y + down);
				texels.push((layer.u + across) / atlasWidth, (layer.v + down) / atlasHeight);
			}
		}

		for (let row = 0; row < rows; row++) {
			for (let column = 0; column < columns; column++) {
				const corner = first + row * (columns + 1) + column;

				indices.push(corner, corner + 1, corner + columns + 1, corner + 1, corner + columns + 2, corner + columns + 1);
			}
		}

		spans.push({ name: layer.name, first, count: (columns + 1) * (rows + 1) });
	}

	const program = gl.createProgram()!;

	gl.attachShader(program, compile(gl, gl.VERTEX_SHADER, VERTEX_SHADER));
	gl.attachShader(program, compile(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER));
	gl.linkProgram(program);
	gl.useProgram(program);

	const positions = new Float32Array(base);
	const positionBuffer = gl.createBuffer();
	const positionSlot = gl.getAttribLocation(program, 'position');

	gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
	gl.bufferData(gl.ARRAY_BUFFER, positions, gl.DYNAMIC_DRAW);
	gl.enableVertexAttribArray(positionSlot);
	gl.vertexAttribPointer(positionSlot, 2, gl.FLOAT, false, 0, 0);

	const texelSlot = gl.getAttribLocation(program, 'texel');

	gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(texels), gl.STATIC_DRAW);
	gl.enableVertexAttribArray(texelSlot);
	gl.vertexAttribPointer(texelSlot, 2, gl.FLOAT, false, 0, 0);

	gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, gl.createBuffer());
	gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(indices), gl.STATIC_DRAW);

	// premultiplied on upload, so the soft edges of a layer never pick up a dark fringe
	gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
	gl.bindTexture(gl.TEXTURE_2D, gl.createTexture());
	gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, atlas);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
	gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

	gl.uniform4f(gl.getUniformLocation(program, 'view'), VIEW.x, VIEW.y, VIEW.width, VIEW.height);
	gl.enable(gl.BLEND);
	gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
	gl.clearColor(0, 0, 0, 0);

	const pose: Pose = { angleX: 0, angleY: 0, lookX: 0, lookY: 0, breath: 0, eyeOpen: 1, wind: 1 };
	const springs: Springs = { hair: 0, hairSpeed: 0, skirt: 0, skirtSpeed: 0, lastAngleX: 0 };
	const point: Point = { x: 0, y: 0 };

	function resize(): void {
		const ratio = Math.min(window.devicePixelRatio || 1, MAX_PIXEL_RATIO);
		const width = Math.round(canvas.clientWidth * ratio);
		const height = Math.round(canvas.clientHeight * ratio);

		if (canvas.width !== width || canvas.height !== height) {
			canvas.width = width;
			canvas.height = height;
		}

		gl!.viewport(0, 0, canvas.width, canvas.height);
	}

	/** Hair and skirt are pulled by the head's turning and by a slow gust, and overshoot on the way back. */
	function swing(seconds: number, delta: number): void {
		const step = Math.min(delta, 0.05);
		const turning = step > 0
			? (pose.angleX - springs.lastAngleX) / step
			: 0;
		const gust = (Math.sin(seconds * 0.7) + Math.sin(seconds * 1.9 + 1.3) * 0.5) * 0.12 * pose.wind;

		springs.lastAngleX = pose.angleX;

		springs.hairSpeed += ((gust - turning * 0.16 - springs.hair) * 38 - springs.hairSpeed * 5) * step;
		springs.hair += springs.hairSpeed * step;

		springs.skirtSpeed += ((gust * 0.7 - turning * 0.08 - springs.skirt) * 26 - springs.skirtSpeed * 4) * step;
		springs.skirt += springs.skirtSpeed * step;
	}

	function render(seconds: number, deltaSeconds: number): void {
		swing(seconds, deltaSeconds);

		const frame: Frame = {
			...pose,
			time: seconds,
			hair: springs.hair,
			skirt: springs.skirt,
			tilt: pose.angleX * TILT
		};

		for (const span of spans) {
			for (let vertex = span.first; vertex < span.first + span.count; vertex++) {
				point.x = base[vertex * 2]!;
				point.y = base[vertex * 2 + 1]!;
				bend(span.name, point, frame);
				positions[vertex * 2] = point.x;
				positions[vertex * 2 + 1] = point.y;
			}
		}

		gl!.bindBuffer(gl!.ARRAY_BUFFER, positionBuffer);
		gl!.bufferSubData(gl!.ARRAY_BUFFER, 0, positions);
		gl!.clear(gl!.COLOR_BUFFER_BIT);
		gl!.drawElements(gl!.TRIANGLES, indices.length, gl!.UNSIGNED_SHORT, 0);
	}

	function destroy(): void {
		gl!.getExtension('WEBGL_lose_context')?.loseContext();
	}

	resize();

	return { pose, render, resize, destroy };
}
