import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function ThreeDataGlobe() {
  const mountRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const mount = mountRef.current;
    if (!mount) return;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.set(0, 0, 4.2);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    mount.appendChild(renderer.domElement);

    const group = new THREE.Group();
    scene.add(group);

    const sphere = new THREE.Mesh(
      new THREE.IcosahedronGeometry(1.24, 3),
      new THREE.MeshBasicMaterial({ color: 0x38bdf8, wireframe: true, transparent: true, opacity: 0.2 }),
    );
    group.add(sphere);

    const pointGeometry = new THREE.BufferGeometry();
    const count = 420;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i += 1) {
      const radius = 1.1 + Math.random() * 0.42;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);
    }
    pointGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const points = new THREE.Points(
      pointGeometry,
      new THREE.PointsMaterial({ color: 0xa78bfa, size: 0.018, transparent: true, opacity: 0.82 }),
    );
    group.add(points);

    const torus = new THREE.Mesh(
      new THREE.TorusGeometry(1.6, 0.006, 8, 180),
      new THREE.MeshBasicMaterial({ color: 0x10b981, transparent: true, opacity: 0.48 }),
    );
    torus.rotation.x = Math.PI / 2.45;
    group.add(torus);

    const resize = () => {
      const { width, height } = mount.getBoundingClientRect();
      renderer.setSize(width, height, false);
      camera.aspect = width / Math.max(height, 1);
      camera.updateProjectionMatrix();
    };
    resize();

    const observer = new ResizeObserver(resize);
    observer.observe(mount);

    let frame = 0;
    const animate = () => {
      frame = requestAnimationFrame(animate);
      group.rotation.y += 0.0038;
      points.rotation.y -= 0.0015;
      torus.rotation.z += 0.0022;
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      cancelAnimationFrame(frame);
      observer.disconnect();
      renderer.dispose();
      sphere.geometry.dispose();
      sphere.material.dispose();
      pointGeometry.dispose();
      points.material.dispose();
      torus.geometry.dispose();
      torus.material.dispose();
      mount.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-[2rem]" aria-hidden="true">
      <div className="absolute -right-20 -top-16 h-80 w-80 opacity-70 blur-3xl bg-cyan-400/30 dark:bg-cyan-500/20" />
      <div className="absolute -bottom-24 left-4 h-72 w-72 opacity-60 blur-3xl bg-violet-500/25 dark:bg-violet-500/20" />
      <div ref={mountRef} className="absolute right-[-70px] top-[-35px] hidden h-[360px] w-[360px] sm:block lg:right-[-20px] lg:top-[-10px]" />
    </div>
  );
}
