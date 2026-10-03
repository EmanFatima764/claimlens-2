"use client";

import { useEffect, useRef, useState } from "react";
import { Mesh, Program, Renderer, Triangle } from "ogl";

type RaysOrigin =
  | "top-center"
  | "top-left"
  | "top-right"
  | "right"
  | "left"
  | "bottom-center"
  | "bottom-right"
  | "bottom-left";

interface LightRaysProps {
  raysOrigin?: RaysOrigin;
  raysColor?: string;
  raysSpeed?: number;
  lightSpread?: number;
  rayLength?: number;
  pulsating?: boolean;
  fadeDistance?: number;
  saturation?: number;
  followMouse?: boolean;
  mouseInfluence?: number;
  noiseAmount?: number;
  distortion?: number;
  className?: string;
}

type Vec2 = [number, number];
type Vec3 = [number, number, number];

interface Uniforms {
  iTime: { value: number };
  iResolution: { value: Vec2 };
  rayPos: { value: Vec2 };
  rayDir: { value: Vec2 };
  raysColor: { value: Vec3 };
  raysSpeed: { value: number };
  lightSpread: { value: number };
  rayLength: { value: number };
  pulsating: { value: number };
  fadeDistance: { value: number };
  saturation: { value: number };
  mousePos: { value: Vec2 };
  mouseInfluence: { value: number };
  noiseAmount: { value: number };
  distortion: { value: number };
}

function hexToRgb(hex: string): Vec3 {
  const match = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return match
    ? [parseInt(match[1], 16) / 255, parseInt(match[2], 16) / 255, parseInt(match[3], 16) / 255]
    : [1, 1, 1];
}

function getPlacement(origin: RaysOrigin, width: number, height: number) {
  const outside = 0.2;
  switch (origin) {
    case "top-left": return { position: [0, -outside * height] as Vec2, direction: [0.7, 0.7] as Vec2 };
    case "top-right": return { position: [width, -outside * height] as Vec2, direction: [-0.7, 0.7] as Vec2 };
    case "left": return { position: [-outside * width, 0.5 * height] as Vec2, direction: [1, 0] as Vec2 };
    case "right": return { position: [(1 + outside) * width, 0.5 * height] as Vec2, direction: [-1, 0] as Vec2 };
    case "bottom-left": return { position: [0, (1 + outside) * height] as Vec2, direction: [0.7, -0.7] as Vec2 };
    case "bottom-center": return { position: [0.5 * width, (1 + outside) * height] as Vec2, direction: [0, -1] as Vec2 };
    case "bottom-right": return { position: [width, (1 + outside) * height] as Vec2, direction: [-0.7, -0.7] as Vec2 };
    default: return { position: [0.5 * width, -outside * height] as Vec2, direction: [0, 1] as Vec2 };
  }
}

const vertex = `
  attribute vec2 position;
  varying vec2 vUv;
  void main() {
    vUv = position * 0.5 + 0.5;
    gl_Position = vec4(position, 0.0, 1.0);
  }
`;

const fragment = `
  precision highp float;
  uniform float iTime;
  uniform vec2 iResolution;
  uniform vec2 rayPos;
  uniform vec2 rayDir;
  uniform vec3 raysColor;
  uniform float raysSpeed;
  uniform float lightSpread;
  uniform float rayLength;
  uniform float pulsating;
  uniform float fadeDistance;
  uniform float saturation;
  uniform vec2 mousePos;
  uniform float mouseInfluence;
  uniform float noiseAmount;
  uniform float distortion;
  varying vec2 vUv;

  float noise(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
  }

  float smoothNoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    
    float a = noise(i);
    float b = noise(i + vec2(1.0, 0.0));
    float c = noise(i + vec2(0.0, 1.0));
    float d = noise(i + vec2(1.0, 1.0));
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
  }

  void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy;
    
    float t = iTime * raysSpeed * 0.3;
    
    // Center position (bottom center)
    vec2 center = vec2(0.5, 0.0);
    vec2 toPixel = uv - center;
    
    // Distance from bottom center
    float dist = length(toPixel);
    
    // Angle from center
    float angle = atan(toPixel.x, toPixel.y);
    
    // Create multiple rotating beams
    float beams = 0.0;
    float numBeams = 16.0;
    
    for(float i = 0.0; i < numBeams; i++) {
      float beamAngle = (i / numBeams) * 6.28318;
      float rotation = t * 0.5;
      float currentAngle = beamAngle + rotation;
      
      // Calculate beam strength based on angle difference
      float angleDiff = angle - currentAngle;
      angleDiff = mod(angleDiff + 3.14159, 6.28318) - 3.14159;
      
      // Create beam with smooth falloff
      float beamWidth = lightSpread * 0.15;
      float beam = smoothstep(beamWidth, 0.0, abs(angleDiff));
      
      // Add some noise variation to each beam
      float noiseVal = smoothNoise(vec2(i * 10.0 + t * 2.0, dist * 3.0));
      beam *= (0.6 + 0.4 * noiseVal);
      
      beams += beam;
    }
    
    // Normalize beams
    beams = clamp(beams * 0.3, 0.0, 1.0);
    
    // Distance-based falloff (stronger near bottom, fades upward)
    float falloff = 1.0 - smoothstep(0.0, rayLength * 0.5, dist);
    falloff = pow(falloff, 0.7);
    
    // Add glow at the center
    float centerGlow = 1.0 / (1.0 + dist * 2.0);
    centerGlow = pow(centerGlow, 2.0) * 1.5;
    
    // Combine beams and center glow
    float intensity = (beams * falloff + centerGlow * 0.3) * rayLength;
    
    // Add circular wave patterns
    float wave1 = sin(dist * 8.0 - t * 3.0) * 0.5 + 0.5;
    float wave2 = sin(dist * 12.0 + t * 2.0) * 0.5 + 0.5;
    float waves = (wave1 * 0.6 + wave2 * 0.4) * 0.3;
    
    intensity += waves * falloff;
    
    // Pulsating effect
    float pulse = sin(t * 2.0) * 0.1 + 0.9;
    intensity *= pulse;
    
    // Apply color
    vec3 color = raysColor * intensity;
    
    // Add bright highlights
    float highlight = pow(intensity, 3.0);
    color += vec3(highlight * 0.6, highlight * 0.7, highlight * 0.9);
    
    // Smooth alpha
    float alpha = clamp(intensity * saturation, 0.0, 1.0);
    
    gl_FragColor = vec4(color, alpha);
  }
`;

export default function LightRays({
  raysOrigin = "top-center",
  raysColor = "#62d7ff",
  raysSpeed = 0.65,
  lightSpread = 1.2,
  rayLength = 1.8,
  pulsating = true,
  fadeDistance = 1,
  saturation = 1,
  followMouse = true,
  mouseInfluence = 0.14,
  noiseAmount = 0.015,
  distortion = 0.05,
  className = "",
}: LightRaysProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mouseRef = useRef({ x: 0.5, y: 0.5 });
  const smoothMouseRef = useRef({ x: 0.5, y: 0.5 });
  const animationRef = useRef<number | null>(null);
  const rendererRef = useRef<Renderer | null>(null);
  const uniformsRef = useRef<Uniforms | null>(null);
  const meshRef = useRef<Mesh | null>(null);
  const cleanupFunctionRef = useRef<(() => void) | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Intersection Observer for performance optimization
  useEffect(() => {
    if (!containerRef.current) return;

    observerRef.current = new IntersectionObserver(
      (entries) => {
        const entry = entries[0];
        setIsVisible(entry.isIntersecting);
      },
      { threshold: 0.1 }
    );

    observerRef.current.observe(containerRef.current);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
        observerRef.current = null;
      }
    };
  }, []);

  // WebGL initialization and animation
  useEffect(() => {
    if (!isVisible || !containerRef.current) return;

    if (cleanupFunctionRef.current) {
      cleanupFunctionRef.current();
      cleanupFunctionRef.current = null;
    }

    const initializeWebGL = async () => {
      if (!containerRef.current) return;

      await new Promise((resolve) => setTimeout(resolve, 10));
      if (!containerRef.current) return;

      const renderer = new Renderer({
        dpr: Math.min(window.devicePixelRatio, 2),
        alpha: true,
      });
      rendererRef.current = renderer;

      const gl = renderer.gl;
      gl.canvas.style.width = "100%";
      gl.canvas.style.height = "100%";
      gl.canvas.style.display = "block";

      while (containerRef.current.firstChild) {
        containerRef.current.removeChild(containerRef.current.firstChild);
      }
      containerRef.current.appendChild(gl.canvas);

      const uniforms: Uniforms = {
        iTime: { value: 0 },
        iResolution: { value: [1, 1] },
        rayPos: { value: [0, 0] },
        rayDir: { value: [0, 1] },
        raysColor: { value: hexToRgb(raysColor) },
        raysSpeed: { value: raysSpeed },
        lightSpread: { value: lightSpread },
        rayLength: { value: rayLength },
        pulsating: { value: pulsating ? 1 : 0 },
        fadeDistance: { value: fadeDistance },
        saturation: { value: saturation },
        mousePos: { value: [0.5, 0.5] },
        mouseInfluence: { value: mouseInfluence },
        noiseAmount: { value: noiseAmount },
        distortion: { value: distortion },
      };
      uniformsRef.current = uniforms;

      const mesh = new Mesh(gl, {
        geometry: new Triangle(gl),
        program: new Program(gl, {
          vertex,
          fragment,
          uniforms,
          transparent: true,
        }),
      });
      meshRef.current = mesh;

      const updatePlacement = () => {
        if (!containerRef.current || !renderer) return;
        const { clientWidth: wCSS, clientHeight: hCSS } = containerRef.current;
        renderer.setSize(wCSS, hCSS);
        const dpr = renderer.dpr;
        const w = wCSS * dpr;
        const h = hCSS * dpr;
        uniforms.iResolution.value = [w, h];
        const placement = getPlacement(raysOrigin, w, h);
        uniforms.rayPos.value = placement.position;
        uniforms.rayDir.value = placement.direction;
      };

      const loop = (t: number) => {
        if (!rendererRef.current || !uniformsRef.current || !meshRef.current) return;

        uniforms.iTime.value = t * 0.001;

        // Smooth mouse following
        if (followMouse && mouseInfluence > 0.0) {
          const smoothing = 0.95;
          smoothMouseRef.current.x =
            smoothMouseRef.current.x * smoothing + mouseRef.current.x * (1 - smoothing);
          smoothMouseRef.current.y =
            smoothMouseRef.current.y * smoothing + mouseRef.current.y * (1 - smoothing);
          uniforms.mousePos.value = [
            smoothMouseRef.current.x,
            1.0 - smoothMouseRef.current.y,
          ];
        }

        renderer.render({ scene: mesh });
        animationRef.current = requestAnimationFrame(loop);
      };

      window.addEventListener("resize", updatePlacement);
      updatePlacement();
      animationRef.current = requestAnimationFrame(loop);

      cleanupFunctionRef.current = () => {
        if (animationRef.current) cancelAnimationFrame(animationRef.current);
        window.removeEventListener("resize", updatePlacement);
        if (renderer.gl.canvas.parentNode) {
          renderer.gl.canvas.parentNode.removeChild(renderer.gl.canvas);
        }
      };
    };

    initializeWebGL();

    return () => cleanupFunctionRef.current?.();
  }, [
    isVisible,
    raysOrigin,
    raysColor,
    raysSpeed,
    lightSpread,
    rayLength,
    pulsating,
    fadeDistance,
    saturation,
    followMouse,
    mouseInfluence,
    noiseAmount,
    distortion,
  ]);

  // Mouse movement handler
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      mouseRef.current = {
        x: (e.clientX - rect.left) / rect.width,
        y: (e.clientY - rect.top) / rect.height,
      };
    };

    if (followMouse) {
      window.addEventListener("mousemove", handleMouseMove);
      return () => window.removeEventListener("mousemove", handleMouseMove);
    }
  }, [followMouse]);

  return (
    <div
      ref={containerRef}
      className={`light-rays ${className}`}
      aria-hidden="true"
    />
  );
}
