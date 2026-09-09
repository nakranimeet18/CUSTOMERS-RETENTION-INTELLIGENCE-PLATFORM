/**
 * Professional Machine Learning & Neural Data Mesh Background Animation
 * - Retina Display (dpr) razor-sharp rendering
 * - Multi-Geometry AI Nodes: Hexagons, Decision Diamonds, Tensor Squares, and ML Mathematical Glyphs (Σ, f(x), ŷ, λ, Δ)
 * - Autonomous Neural Synapses & Data Transmission Packets
 * - Balanced Light & Dark Harmony (Midnight Navy, Royal Sapphire, Tech Sky Blue, Emerald Retention, Crystal Cyan)
 * - Enterprise Grade: Preserves crisp white base layout for mentor presentation
 */
(function() {
  function initMLBackground() {
    if (document.getElementById('ml-bg-canvas')) return;

    // 1. Ambient Glow Mesh (Subtle, non-intrusive enterprise aura)
    const glowDiv = document.createElement('div');
    glowDiv.className = 'ml-ambient-glow';
    glowDiv.innerHTML = `
      <div class="glow-orb glow-orb-1"></div>
      <div class="glow-orb glow-orb-2"></div>
      <div class="glow-orb glow-orb-3"></div>
    `;
    document.body.insertBefore(glowDiv, document.body.firstChild);

    // 2. High-Performance Canvas with Retina Support
    const canvas = document.createElement('canvas');
    canvas.id = 'ml-bg-canvas';
    document.body.insertBefore(canvas, document.body.firstChild);

    const ctx = canvas.getContext('2d');
    let dpr = window.devicePixelRatio || 1;
    let width = window.innerWidth;
    let height = window.innerHeight;

    function resize() {
      dpr = window.devicePixelRatio || 1;
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
      ctx.scale(dpr, dpr);
      initNodes();
    }

    window.addEventListener('resize', resize);

    // Light & Dark Color Harmony:
    // Navy Slate (dark anchor), Royal Sapphire (primary tech), Sky Blue (vibrant signal), 
    // Crystal Cyan (highlight), Emerald (positive retention metric)
    const PALETTE = [
      { stroke: 'rgba(2, 132, 199, 0.75)', fill: 'rgba(2, 132, 199, 0.10)', glow: '#0284c7', text: 'rgba(2, 132, 199, 0.75)' },
      { stroke: 'rgba(56, 189, 248, 0.85)', fill: 'rgba(56, 189, 248, 0.12)', glow: '#38bdf8', text: 'rgba(14, 165, 233, 0.85)' },
      { stroke: 'rgba(15, 23, 42, 0.60)',   fill: 'rgba(15, 23, 42, 0.06)',   glow: '#0f172a', text: 'rgba(15, 23, 42, 0.55)' },
      { stroke: 'rgba(14, 165, 233, 0.70)', fill: 'rgba(224, 242, 254, 0.20)',glow: '#0ea5e9', text: 'rgba(2, 132, 199, 0.75)' },
      { stroke: 'rgba(16, 185, 129, 0.65)', fill: 'rgba(16, 185, 129, 0.10)', glow: '#10b981', text: 'rgba(16, 185, 129, 0.75)' }
    ];

    const SHAPES = ['hexagon', 'diamond', 'square', 'glyph', 'circle'];
    const ML_GLYPHS = ['f(x)', 'ŷ', 'Σ', 'λ', 'Δ', 'wᵢ', 'x̄', '01'];

    class MLNode {
      constructor() {
        this.reset(true);
      }

      reset(init = false) {
        this.x = Math.random() * width;
        this.y = init ? Math.random() * height : height + 35;
        this.size = Math.random() * 8 + 8; // 8px to 16px
        this.vx = (Math.random() - 0.5) * 0.4;
        this.vy = -(Math.random() * 0.35 + 0.15); // Calm, gentle upward drift
        this.rotation = Math.random() * Math.PI * 2;
        this.vRot = (Math.random() - 0.5) * 0.012;
        this.shape = SHAPES[Math.floor(Math.random() * SHAPES.length)];
        this.glyph = ML_GLYPHS[Math.floor(Math.random() * ML_GLYPHS.length)];
        this.color = PALETTE[Math.floor(Math.random() * PALETTE.length)];
        this.opacity = Math.random() * 0.4 + 0.35;
        this.pulsePhase = Math.random() * Math.PI * 2;
      }

      update() {
        this.x += this.vx;
        this.y += this.vy;
        this.rotation += this.vRot;
        this.pulsePhase += 0.025;

        if (this.y < -40 || this.x < -40 || this.x > width + 40) {
          this.reset(false);
        }
      }

      draw(context) {
        context.save();
        context.translate(this.x, this.y);
        context.rotate(this.rotation);

        const currentOpacity = this.opacity * (0.85 + 0.15 * Math.sin(this.pulsePhase));
        context.globalAlpha = currentOpacity;
        context.strokeStyle = this.color.stroke;
        context.fillStyle = this.color.fill;
        context.lineWidth = 1.3;
        context.shadowColor = this.color.glow;
        context.shadowBlur = 5;

        if (this.shape === 'hexagon') {
          // Hexagonal Data Feature Node
          context.beginPath();
          for (let i = 0; i < 6; i++) {
            const angle = (i * Math.PI) / 3;
            const hx = this.size * Math.cos(angle);
            const hy = this.size * Math.sin(angle);
            if (i === 0) context.moveTo(hx, hy);
            else context.lineTo(hx, hy);
          }
          context.closePath();
          context.fill();
          context.stroke();

          // Inner tech nucleus
          context.beginPath();
          context.arc(0, 0, 1.8, 0, Math.PI * 2);
          context.fillStyle = this.color.stroke;
          context.fill();

        } else if (this.shape === 'diamond') {
          // XGBoost Tree Split Decision Diamond
          context.beginPath();
          context.moveTo(0, -this.size * 1.15);
          context.lineTo(this.size * 0.85, 0);
          context.lineTo(0, this.size * 1.15);
          context.lineTo(-this.size * 0.85, 0);
          context.closePath();
          context.fill();
          context.stroke();

          // Internal split crosshair
          context.beginPath();
          context.moveTo(-this.size * 0.35, 0);
          context.lineTo(this.size * 0.35, 0);
          context.moveTo(0, -this.size * 0.45);
          context.lineTo(0, this.size * 0.45);
          context.lineWidth = 0.8;
          context.stroke();

        } else if (this.shape === 'square') {
          // Tensor Data Matrix Cube
          const half = this.size * 0.72;
          context.fillRect(-half, -half, half * 2, half * 2);
          context.strokeRect(-half, -half, half * 2, half * 2);

          context.beginPath();
          context.arc(0, 0, 1.5, 0, Math.PI * 2);
          context.fillStyle = this.color.stroke;
          context.fill();

        } else if (this.shape === 'glyph') {
          // Machine Learning Mathematical Formula Symbol
          context.rotate(-this.rotation); // Keep text readable horizontally
          context.font = `600 ${Math.max(10, this.size * 0.95)}px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace`;
          context.fillStyle = this.color.text;
          context.textAlign = 'center';
          context.textBaseline = 'middle';
          context.fillText(this.glyph, 0, 0);

        } else {
          // Synapse Node Circle
          context.beginPath();
          context.arc(0, 0, this.size * 0.55, 0, Math.PI * 2);
          context.fill();
          context.stroke();

          context.beginPath();
          context.arc(0, 0, 1.8, 0, Math.PI * 2);
          context.fillStyle = '#ffffff';
          context.fill();
        }

        context.restore();
      }
    }

    // High-speed Data Transmission Packet along synapses
    class DataPulse {
      constructor(fromNode, toNode) {
        this.from = fromNode;
        this.to = toNode;
        this.progress = 0;
        this.speed = Math.random() * 0.018 + 0.012;
      }

      update() {
        this.progress += this.speed;
        return this.progress < 1;
      }

      draw(context) {
        const cx = this.from.x + (this.to.x - this.from.x) * this.progress;
        const cy = this.from.y + (this.to.y - this.from.y) * this.progress;

        context.save();
        context.shadowColor = '#38bdf8';
        context.shadowBlur = 8;
        context.fillStyle = '#ffffff';
        context.beginPath();
        context.arc(cx, cy, 2.2, 0, Math.PI * 2);
        context.fill();
        context.restore();
      }
    }

    let nodes = [];
    let pulses = [];

    function initNodes() {
      const nodeCount = Math.floor((width * height) / 26000);
      const count = Math.min(Math.max(nodeCount, 28), 65);
      nodes = [];
      for (let i = 0; i < count; i++) {
        nodes.push(new MLNode());
      }
    }

    // Proximity Synapse Distance
    const MAX_DIST = 145;

    // Gentle mouse interaction
    let mouseX = -1000;
    let mouseY = -1000;
    window.addEventListener('mousemove', (e) => {
      mouseX = e.clientX;
      mouseY = e.clientY;
    });

    resize();

    function render() {
      ctx.clearRect(0, 0, width, height);

      // 1. Draw Synapses
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < MAX_DIST) {
            const alpha = (1 - dist / MAX_DIST) * 0.28;
            ctx.save();
            ctx.strokeStyle = `rgba(2, 132, 199, ${alpha})`;
            ctx.lineWidth = 0.9;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
            ctx.restore();

            // Periodic ML data packet transmission
            if (Math.random() < 0.0007 && pulses.length < 10) {
              pulses.push(new DataPulse(nodes[i], nodes[j]));
            }
          }
        }

        // Proximity synapse to mouse
        const mdx = nodes[i].x - mouseX;
        const mdy = nodes[i].y - mouseY;
        const mdist = Math.sqrt(mdx * mdx + mdy * mdy);
        if (mdist < 150) {
          const mAlpha = (1 - mdist / 150) * 0.4;
          ctx.save();
          ctx.strokeStyle = `rgba(56, 189, 248, ${mAlpha})`;
          ctx.lineWidth = 1.1;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(mouseX, mouseY);
          ctx.stroke();
          ctx.restore();
        }
      }

      // 2. Draw Transmitting Data Pulses
      for (let p = pulses.length - 1; p >= 0; p--) {
        if (!pulses[p].update()) {
          pulses.splice(p, 1);
        } else {
          pulses[p].draw(ctx);
        }
      }

      // 3. Draw ML Nodes
      for (let i = 0; i < nodes.length; i++) {
        nodes[i].update();
        nodes[i].draw(ctx);
      }

      requestAnimationFrame(render);
    }

    requestAnimationFrame(render);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMLBackground);
  } else {
    initMLBackground();
  }
})();
