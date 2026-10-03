"use client";

import { useEffect, useRef } from "react";

interface AuroraBackgroundProps {
  color?: string;
  speed?: number;
  intensity?: number;
  className?: string;
}

export default function AuroraBackground({
  color = "#00ffff",
  speed = 1.0,
  intensity = 2.0,
  className = "",
}: AuroraBackgroundProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const mouseRef = useRef({ x: 0.5, y: 0.5 });
  const smoothMouseRef = useRef({ x: 0.5, y: 0.5 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext("webgl", { alpha: true, premultipliedAlpha: false });
    if (!gl) {
      console.error("WebGL not supported");
      return;
    }

    // Vertex shader
    const vertexShaderSource = `
      attribute vec2 position;
      void main() {
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `;

    // Fragment shader with flowing aurora ribbons and pointer distortion.
    const fragmentShaderSource = `
      precision mediump float;
      uniform float u_time;
      uniform vec2 u_resolution;
      uniform vec3 u_color;
      uniform float u_intensity;
      uniform vec2 u_mouse;

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

      float fbm(vec2 p) {
        float value = 0.0;
        float amplitude = 0.5;
        for (int i = 0; i < 4; i++) {
          value += amplitude * smoothNoise(p);
          p = p * 2.02 + 17.3;
          amplitude *= 0.5;
        }
        return value;
      }

      void main() {
        vec2 uv = gl_FragCoord.xy / u_resolution.xy;
        float t = u_time * 0.42;
        vec2 pointer = (u_mouse - 0.5) * vec2(0.28, 0.16);
        vec2 p = uv + pointer;
        float horizon = smoothstep(0.02, 0.68, 1.0 - uv.y);
        float atmosphere = 1.0 - smoothstep(0.15, 1.0, uv.y);
        float movement = fbm(vec2(p.x * 2.1 + t * 0.18, p.y * 1.7 - t * 0.12));
        float ribbonA = sin(p.x * 7.0 + movement * 4.0 + t) * 0.5 + 0.5;
        float ribbonB = sin(p.x * 11.0 - movement * 5.0 - t * 0.7) * 0.5 + 0.5;
        float waveA = exp(-abs(uv.y - (0.74 + (ribbonA - 0.5) * 0.22)) * 22.0);
        float waveB = exp(-abs(uv.y - (0.58 + (ribbonB - 0.5) * 0.18)) * 28.0);
        float waveC = exp(-abs(uv.y - (0.38 + sin(p.x * 5.0 - t) * 0.12)) * 34.0);
        float glow = (waveA * 0.95 + waveB * 0.62 + waveC * 0.38) * atmosphere;
        glow += pow(max(0.0, 1.0 - length(uv - vec2(0.5 + pointer.x, 0.05))), 3.0) * 0.5;
        glow *= (0.7 + movement * 0.55) * u_intensity;
        glow *= horizon;
        float pulse = 0.9 + sin(t * 1.7) * 0.1;
        glow *= pulse;
        vec3 aurora = mix(u_color, vec3(0.16, 0.95, 0.82), 0.22);
        vec3 color = aurora * glow;
        color += vec3(0.04, 0.34, 0.32) * pow(glow, 2.0);
        gl_FragColor = vec4(color, clamp(glow * 0.9, 0.0, 0.92));
      }
    `;

    // Compile shader
    function createShader(gl: WebGLRenderingContext, type: number, source: string): WebGLShader | null {
      const shader = gl.createShader(type);
      if (!shader) return null;
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error("Shader compile error:", gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
      }
      return shader;
    }

    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

    if (!vertexShader || !fragmentShader) return;

    // Create program
    const program = gl.createProgram();
    if (!program) return;

    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error("Program link error:", gl.getProgramInfoLog(program));
      return;
    }

    gl.useProgram(program);

    // Create fullscreen quad
    const positions = new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]);
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, positions, gl.STATIC_DRAW);

    const positionLocation = gl.getAttribLocation(program, "position");
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    // Get uniform locations
    const timeLocation = gl.getUniformLocation(program, "u_time");
    const resolutionLocation = gl.getUniformLocation(program, "u_resolution");
    const colorLocation = gl.getUniformLocation(program, "u_color");
    const intensityLocation = gl.getUniformLocation(program, "u_intensity");
    const mouseLocation = gl.getUniformLocation(program, "u_mouse");

    // Parse color
    const hexToRgb = (hex: string): [number, number, number] => {
      const match = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return match
        ? [parseInt(match[1], 16) / 255, parseInt(match[2], 16) / 255, parseInt(match[3], 16) / 255]
        : [0, 1, 1];
    };

    const rgbColor = hexToRgb(color);
    const activeColorRef = { current: rgbColor };
    const themeColors: Record<string, string> = {
      aurora: "#00eaff",
      coral: "#ff765f",
      mint: "#45e0ae",
    };
    const themeObserver = new MutationObserver(() => {
      const selectedTheme = document.documentElement.dataset.theme || "aurora";
      activeColorRef.current = hexToRgb(themeColors[selectedTheme] || themeColors.aurora);
    });
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

    const handleMouseMove = (event: MouseEvent) => {
      mouseRef.current = {
        x: event.clientX / window.innerWidth,
        y: event.clientY / window.innerHeight,
      };
    };

    // Resize canvas
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio, 2);
      canvas.width = canvas.clientWidth * dpr;
      canvas.height = canvas.clientHeight * dpr;
      gl.viewport(0, 0, canvas.width, canvas.height);
    };

    resize();
    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", handleMouseMove);

    // Enable blending
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

    // Animation loop
    const startTime = Date.now();
    const animate = () => {
      const currentTime = (Date.now() - startTime) * 0.001 * speed;

      gl.clearColor(0, 0, 0, 0);
      gl.clear(gl.COLOR_BUFFER_BIT);

      gl.uniform1f(timeLocation, currentTime);
      gl.uniform2f(resolutionLocation, canvas.width, canvas.height);
      const activeColor = activeColorRef.current;
      gl.uniform3f(colorLocation, activeColor[0], activeColor[1], activeColor[2]);
      gl.uniform1f(intensityLocation, intensity);
      smoothMouseRef.current.x += (mouseRef.current.x - smoothMouseRef.current.x) * 0.035;
      smoothMouseRef.current.y += (mouseRef.current.y - smoothMouseRef.current.y) * 0.035;
      gl.uniform2f(mouseLocation, smoothMouseRef.current.x, smoothMouseRef.current.y);

      gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", handleMouseMove);
      themeObserver.disconnect();
      if (animationRef.current) cancelAnimationFrame(animationRef.current);
      gl.deleteProgram(program);
      gl.deleteShader(vertexShader);
      gl.deleteShader(fragmentShader);
      gl.deleteBuffer(buffer);
    };
  }, [color, speed, intensity]);

  return (
    <canvas
      ref={canvasRef}
      className={`aurora-background ${className}`}
      style={{ zIndex: 0, mixBlendMode: "screen", opacity: 1 }}
    />
  );
}
