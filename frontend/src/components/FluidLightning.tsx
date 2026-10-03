"use client";

import { useEffect, useRef, useState } from "react";
import { Mesh, Program, Renderer, Triangle } from "ogl";

interface FluidLightningProps {
  primaryColor?: string;
  secondaryColor?: string;
  speed?: number;
  intensity?: number;
  complexity?: number;
  className?: string;
}

type Vec2 = [number, number];
type Vec3 = [number, number, number];

interface Uniforms {
  iTime: { value: number };
  iResolution: { value: Vec2 };
  primaryColor: { value: Vec3 };
  secondaryColor: { value: Vec3 };
  speed: { value: number };
  intensity: { value: number };
  complexity: { value: number };
}

function hexToRgb(hex: string): Vec3 {
  const match = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return match
    ? [parseInt(match[1], 16) / 255, parseInt(match[2], 16) / 255, parseInt(match[3], 16) / 255]
    : [0, 1, 1];
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
  uniform vec3 primaryColor;
  uniform vec3 secondaryColor;
  uniform float speed;
  uniform float intensity;
  uniform float complexity;
  varying vec2 vUv;

  // Improved noise function
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

  // Fractal Brownian Motion for organic patterns
  float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for(int i = 0; i < 6; i++) {
      value += amplitude * smoothNoise(p * frequency);
      frequency *= 2.0;
      amplitude *= 0.5;
    }
    return value;
  }

  // Create flowing, circular aurora effect
  vec3 createAurora(vec2 uv) {
    vec2 p = uv * 2.0 - 1.0;
    p.x *= iResolution.x / iResolution.y;
    
    float t = iTime * speed * 0.3;
    
    // Create multiple flowing layers
    float flow1 = fbm(vec2(p.x * 1.5 + t * 0.4, p.y * 1.2 + sin(t * 0.3) * 0.5));
    float flow2 = fbm(vec2(p.x * 2.0 - t * 0.3, p.y * 1.5 + cos(t * 0.4) * 0.6));
    float flow3 = fbm(vec2(p.x * 1.2 + sin(t * 0.5) * 0.4, p.y * 2.0 - t * 0.2));
    
    // Circular wave patterns
    float dist = length(p);
    float wave1 = sin(dist * 3.0 - t * 2.0) * 0.5 + 0.5;
    float wave2 = sin(dist * 5.0 + t * 1.5) * 0.5 + 0.5;
    
    // Combine flows with circular patterns
    float pattern = (flow1 * 0.4 + flow2 * 0.3 + flow3 * 0.3);
    pattern *= (wave1 * 0.6 + wave2 * 0.4);
    
    // Add vertical gradient (stronger at bottom, flowing upward)
    float verticalGradient = smoothstep(0.0, 0.6, 1.0 - uv.y);
    pattern *= verticalGradient;
    
    // Create flowing columns/beams
    float columns = 0.0;
    for(float i = 0.0; i < complexity; i++) {
      float angle = (i / complexity) * 6.28318 + t * 0.5;
      vec2 dir = vec2(cos(angle), sin(angle));
      float beam = smoothstep(0.2, 0.0, abs(dot(normalize(p), dir) - 0.3));
      columns += beam * (sin(t * 2.0 + i) * 0.5 + 0.5);
    }
    
    pattern += columns * 0.3;
    
    // Enhance brightness at center/bottom
    float centerGlow = 1.0 / (1.0 + dist * 0.5);
    pattern *= mix(1.0, centerGlow, 0.4);
    
    // Pulsating effect
    float pulse = (sin(t * 1.5) * 0.15 + 0.85);
    pattern *= pulse;
    
    // Color mixing with gradient
    vec3 color1 = primaryColor * pattern * intensity;
    vec3 color2 = secondaryColor * pattern * intensity * 0.8;
    
    vec3 finalColor = mix(color1, color2, smoothNoise(p * 3.0 + t));
    
    // Add some bright highlights
    float highlight = pow(pattern, 3.0) * 2.0;
    finalColor += vec3(highlight * 0.5, highlight * 0.6, highlight * 0.8);
    
    return finalColor;
  }

  void main() {
    vec2 uv = gl_FragCoord.xy / iResolution.xy;
    
    vec3 color = createAurora(uv);
    
    // Smooth alpha based on intensity
    float alpha = clamp(length(color) * 0.8, 0.0, 1.0);
    
    gl_FragColor = vec4(color, alpha);
  }
`;

export default function FluidLightning({
  primaryColor = "#00ffff",
  secondaryColor = "#0088ff",
  speed = 1.0,
  intensity = 1.5,
  complexity = 8.0,
  className = "",
}: FluidLightningProps) {
  const containerRef = useRef<HTMLDivElement>(null);
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
        primaryColor: { value: hexToRgb(primaryColor) },
        secondaryColor: { value: hexToRgb(secondaryColor) },
        speed: { value: speed },
        intensity: { value: intensity },
        complexity: { value: complexity },
      };
      uniformsRef.current = uniforms;

      const geometry = new Triangle(gl);
      const program = new Program(gl, {
        vertex,
        fragment,
        uniforms,
        transparent: true,
      });

      const mesh = new Mesh(gl, { geometry, program });
      meshRef.current = mesh;

      const updateSize = () => {
        if (!containerRef.current || !renderer) return;
        const { clientWidth: wCSS, clientHeight: hCSS } = containerRef.current;
        renderer.setSize(wCSS, hCSS);
        const dpr = renderer.dpr;
        const w = wCSS * dpr;
        const h = hCSS * dpr;
        uniforms.iResolution.value = [w, h];
      };

      const loop = (t: number) => {
        if (!rendererRef.current || !uniformsRef.current || !meshRef.current) return;

        const uniforms = uniformsRef.current;
        const renderer = rendererRef.current;
        const mesh = meshRef.current;

        uniforms.iTime.value = t * 0.001;
        
        // Clear and render
        const gl = renderer.gl;
        gl.clearColor(0, 0, 0, 0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        
        // Bind and draw the mesh
        mesh.program.uniforms = uniforms;
        mesh.draw();
        
        animationRef.current = requestAnimationFrame(loop);
      };

      window.addEventListener("resize", updateSize);
      updateSize();
      animationRef.current = requestAnimationFrame(loop);

      cleanupFunctionRef.current = () => {
        if (animationRef.current) cancelAnimationFrame(animationRef.current);
        window.removeEventListener("resize", updateSize);
        if (renderer.gl.canvas.parentNode) {
          renderer.gl.canvas.parentNode.removeChild(renderer.gl.canvas);
        }
      };
    };

    initializeWebGL();

    return () => cleanupFunctionRef.current?.();
  }, [isVisible, primaryColor, secondaryColor, speed, intensity, complexity]);

  return (
    <div
      ref={containerRef}
      className={`fluid-lightning ${className}`}
      aria-hidden="true"
    />
  );
}

