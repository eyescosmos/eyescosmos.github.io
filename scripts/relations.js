(function () {
  const canvas = document.getElementById('constellation-canvas');
  const ctx = canvas.getContext('2d');
  const labelEl = document.getElementById('focus-label');
  const metaEl = document.getElementById('focus-meta');
  const hintEl = document.getElementById('focus-hint');
  const fadeEl = document.getElementById('page-fade');
  const prefersCoarse = window.matchMedia('(pointer: coarse)').matches;

  const palette = {
    photographer: '#f1ddc1',
    movement: '#a4c9ff',
    idea: '#d4c1ff',
    label: 'rgba(238, 230, 216, 0.48)',
    labelDim: 'rgba(238, 230, 216, 0.16)',
    activeText: '#f4ece0',
    link: 'rgba(206, 180, 138, 0.58)',
    linkGlow: 'rgba(206, 180, 138, 0.2)'
  };

  const typeLabel = {
    photographer: '写真家',
    movement: '運動',
    idea: '思想'
  };

  const simulation = {
    width: 0,
    height: 0,
    scale: 1,
    cameraX: 0,
    cameraY: 0,
    targetCameraX: 0,
    targetCameraY: 0,
    pointerDown: false,
    dragging: false,
    dragPointerId: null,
    pointerX: 0,
    pointerY: 0,
    dragStartX: 0,
    dragStartY: 0,
    dragStartCameraX: 0,
    dragStartCameraY: 0,
    pressedNodeId: '',
    focusedNodeId: '',
    adjacency: new Map(),
    nodesById: new Map(),
    stars: []
  };

  const nodes = RELATION_GRAPH.nodes.map((node, index) => {
    const angle = (Math.PI * 2 * index) / RELATION_GRAPH.nodes.length;
    const radius = 180 + (index % 4) * 42;
    return {
      ...node,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      vx: 0,
      vy: 0,
      baseRadius: node.type === 'photographer' ? 1.8 : node.type === 'movement' ? 1.5 : 1.3,
      glow: 0,
      hitWidth: node.label.length * 14 + 32
    };
  });

  const links = RELATION_GRAPH.links.map(link => ({
    ...link,
    sourceNode: null,
    targetNode: null
  }));

  nodes.forEach(node => {
    simulation.nodesById.set(node.id, node);
    simulation.adjacency.set(node.id, new Set());
  });

  links.forEach(link => {
    link.sourceNode = simulation.nodesById.get(link.source);
    link.targetNode = simulation.nodesById.get(link.target);
    simulation.adjacency.get(link.source).add(link.target);
    simulation.adjacency.get(link.target).add(link.source);
  });

  function resize() {
    const ratio = window.devicePixelRatio || 1;
    simulation.width = window.innerWidth;
    simulation.height = window.innerHeight;
    canvas.width = simulation.width * ratio;
    canvas.height = simulation.height * ratio;
    canvas.style.width = `${simulation.width}px`;
    canvas.style.height = `${simulation.height}px`;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    simulation.scale = Math.min(simulation.width, simulation.height) / 1000;
    createStars();
  }

  function createStars() {
    simulation.stars = Array.from(
      { length: Math.max(110, Math.round((simulation.width * simulation.height) / 18000)) },
      () => ({
        x: Math.random() * simulation.width,
        y: Math.random() * simulation.height,
        radius: Math.random() * 1.2 + 0.2,
        alpha: Math.random() * 0.34 + 0.06
      })
    );
  }

  function runLayout(iterations) {
    const repulsion = 4400;
    const spring = 0.0062;
    const centering = 0.00045;

    for (let step = 0; step < iterations; step += 1) {
      for (let i = 0; i < nodes.length; i += 1) {
        const a = nodes[i];
        for (let j = i + 1; j < nodes.length; j += 1) {
          const b = nodes[j];
          let dx = b.x - a.x;
          let dy = b.y - a.y;
          let distanceSq = dx * dx + dy * dy;
          if (distanceSq < 0.001) {
            dx = (Math.random() - 0.5) * 0.1;
            dy = (Math.random() - 0.5) * 0.1;
            distanceSq = dx * dx + dy * dy;
          }
          const distance = Math.sqrt(distanceSq);
          const force = repulsion / distanceSq;
          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;
          a.vx -= fx;
          a.vy -= fy;
          b.vx += fx;
          b.vy += fy;
        }
      }

      for (const link of links) {
        const dx = link.targetNode.x - link.sourceNode.x;
        const dy = link.targetNode.y - link.sourceNode.y;
        const distance = Math.max(1, Math.sqrt(dx * dx + dy * dy));
        const desired =
          link.sourceNode.type === 'movement' || link.targetNode.type === 'movement' ? 220 : 170;
        const displacement = distance - desired;
        const fx = (dx / distance) * displacement * spring;
        const fy = (dy / distance) * displacement * spring;
        link.sourceNode.vx += fx;
        link.sourceNode.vy += fy;
        link.targetNode.vx -= fx;
        link.targetNode.vy -= fy;
      }

      for (const node of nodes) {
        node.vx += -node.x * centering;
        node.vy += -node.y * centering;
        node.vx *= 0.74;
        node.vy *= 0.74;
        node.x += node.vx;
        node.y += node.vy;
      }
    }

    for (const node of nodes) {
      node.vx = 0;
      node.vy = 0;
    }
  }

  function getFocusedNode() {
    return simulation.focusedNodeId ? simulation.nodesById.get(simulation.focusedNodeId) : null;
  }

  function setFocusedNode(id) {
    if (!id || simulation.focusedNodeId === id) return;
    simulation.focusedNodeId = id;
    const node = simulation.nodesById.get(id);
    if (node) {
      simulation.targetCameraX = node.x;
      simulation.targetCameraY = node.y;
    }
    updateFocusLabel();
  }

  function worldToScreen(x, y) {
    return {
      x: simulation.width * 0.5 + (x - simulation.cameraX),
      y: simulation.height * 0.5 + (y - simulation.cameraY)
    };
  }

  function findNodeAt(x, y) {
    let best = null;
    let bestScore = Infinity;

    for (const node of nodes) {
      const point = worldToScreen(node.x, node.y);
      const dx = point.x - x;
      const dy = point.y - y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const coreThreshold = 34;
      const labelLeft = point.x + 10;
      const labelTop = point.y - 16;
      const labelRight = labelLeft + node.hitWidth;
      const labelBottom = labelTop + 24;
      const insideLabel = x >= labelLeft && x <= labelRight && y >= labelTop && y <= labelBottom;
      const hit = distance <= coreThreshold || insideLabel;
      if (!hit) continue;

      const rectCx = insideLabel ? (labelLeft + labelRight) * 0.5 : point.x;
      const rectCy = insideLabel ? (labelTop + labelBottom) * 0.5 : point.y;
      const score = Math.hypot(x - rectCx, y - rectCy);
      if (score < bestScore) {
        best = node;
        bestScore = score;
      }
    }

    return best;
  }

  function updateFocusLabel() {
    const node = getFocusedNode();
    if (!node) {
      labelEl.textContent = '関係の星図';
      metaEl.textContent = '星に触れると、その関係だけが静かに立ち上がります。';
      hintEl.textContent = prefersCoarse
        ? 'タップで関係を固定し、もう一度タップで移動します。'
        : 'ホバーで固定、クリックで移動します。';
      return;
    }

    const relatedCount = simulation.adjacency.get(node.id).size;
    labelEl.textContent = node.label;
    metaEl.textContent = `${typeLabel[node.type]} / ${relatedCount}つの接続`;
    hintEl.textContent = prefersCoarse
      ? '別の星をタップすると中心が切り替わります。'
      : '別の星へ移ると中心も静かに入れ替わります。';
  }

  function updateCursor() {
    if (simulation.dragging) {
      canvas.style.cursor = 'grabbing';
      return;
    }
    const node = findNodeAt(simulation.pointerX, simulation.pointerY);
    canvas.style.cursor = node && node.url ? 'pointer' : 'grab';
  }

  function handlePointerDown(event) {
    canvas.setPointerCapture(event.pointerId);
    simulation.pointerDown = true;
    simulation.dragging = false;
    simulation.dragPointerId = event.pointerId;
    simulation.dragStartX = event.clientX;
    simulation.dragStartY = event.clientY;
    simulation.dragStartCameraX = simulation.targetCameraX;
    simulation.dragStartCameraY = simulation.targetCameraY;
    simulation.pointerX = event.clientX;
    simulation.pointerY = event.clientY;
    const node = findNodeAt(event.clientX, event.clientY);
    simulation.pressedNodeId = node ? node.id : '';
    updateCursor();
  }

  function handlePointerMove(event) {
    simulation.pointerX = event.clientX;
    simulation.pointerY = event.clientY;

    if (simulation.pointerDown && simulation.dragPointerId === event.pointerId) {
      const dx = event.clientX - simulation.dragStartX;
      const dy = event.clientY - simulation.dragStartY;
      if (!simulation.dragging && Math.hypot(dx, dy) > 8) {
        simulation.dragging = true;
      }
      if (simulation.dragging) {
        simulation.targetCameraX = simulation.dragStartCameraX - dx;
        simulation.targetCameraY = simulation.dragStartCameraY - dy;
        updateCursor();
        return;
      }
    }

    if (!prefersCoarse) {
      const node = findNodeAt(event.clientX, event.clientY);
      if (node) {
        setFocusedNode(node.id);
      }
    }

    updateCursor();
  }

  function handlePointerLeave() {
    updateCursor();
  }

  function handlePointerUp(event) {
    if (canvas.hasPointerCapture(event.pointerId)) {
      canvas.releasePointerCapture(event.pointerId);
    }

    const wasDragging = simulation.dragging;
    simulation.pointerDown = false;
    simulation.dragPointerId = null;
    simulation.dragging = false;

    if (wasDragging) {
      updateCursor();
      return;
    }

    const node = findNodeAt(event.clientX, event.clientY);
    if (!node || node.id !== simulation.pressedNodeId) {
      simulation.pressedNodeId = '';
      updateCursor();
      return;
    }

    if (prefersCoarse) {
      if (simulation.focusedNodeId === node.id && node.url) {
        navigateTo(node);
      } else {
        setFocusedNode(node.id);
      }
    } else if (node.url) {
      navigateTo(node);
    }

    simulation.pressedNodeId = '';
    updateCursor();
  }

  function navigateTo(node) {
    node.glow = 1.4;
    document.body.classList.add('is-navigating');
    fadeEl.addEventListener('transitionend', () => {
      window.location.href = node.url;
    }, { once: true });
  }

  function getNodeState(node) {
    const focused = getFocusedNode();
    const relatedIds = focused ? simulation.adjacency.get(focused.id) : null;
    if (!focused) {
      return { emphasis: 0.4, active: false, related: false };
    }
    if (focused.id === node.id) {
      return { emphasis: 1, active: true, related: false };
    }
    if (relatedIds.has(node.id)) {
      return { emphasis: 0.68, active: false, related: true };
    }
    return { emphasis: 0.08, active: false, related: false };
  }

  function updateFrameState() {
    const focused = getFocusedNode();
    if (!simulation.pointerDown || !simulation.dragging) {
      if (focused) {
        simulation.targetCameraX = focused.x;
        simulation.targetCameraY = focused.y;
      }
    }
    simulation.cameraX += (simulation.targetCameraX - simulation.cameraX) * 0.065;
    simulation.cameraY += (simulation.targetCameraY - simulation.cameraY) * 0.065;

    for (const node of nodes) {
      node.glow *= 0.86;
    }
  }

  function drawBackground() {
    ctx.clearRect(0, 0, simulation.width, simulation.height);
    const gradient = ctx.createRadialGradient(
      simulation.width * 0.5,
      simulation.height * 0.45,
      0,
      simulation.width * 0.5,
      simulation.height * 0.45,
      simulation.width * 0.6
    );
    gradient.addColorStop(0, 'rgba(18, 20, 28, 0.7)');
    gradient.addColorStop(1, 'rgba(4, 5, 8, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, simulation.width, simulation.height);

    for (const star of simulation.stars) {
      ctx.beginPath();
      ctx.fillStyle = `rgba(255, 248, 238, ${star.alpha})`;
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  function drawLinks() {
    const focused = getFocusedNode();
    if (!focused) return;

    for (const link of links) {
      const active = link.source === focused.id || link.target === focused.id;
      if (!active) continue;

      const start = worldToScreen(link.sourceNode.x, link.sourceNode.y);
      const end = worldToScreen(link.targetNode.x, link.targetNode.y);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.strokeStyle = palette.link;
      ctx.lineWidth = 0.85;
      ctx.globalAlpha = 0.8;
      ctx.shadowBlur = 10;
      ctx.shadowColor = palette.linkGlow;
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    ctx.globalAlpha = 1;
  }

  function drawNode(node, state) {
    const point = worldToScreen(node.x, node.y);
    const radius = node.baseRadius + (state.active ? 3.5 : state.related ? 1.4 : 0) + node.glow;

    ctx.beginPath();
    ctx.fillStyle = palette[node.type];
    ctx.globalAlpha = 0.16 + state.emphasis * 0.82;
    ctx.shadowBlur = 10 + state.emphasis * 16;
    ctx.shadowColor = palette[node.type];
    ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.fillStyle = '#ffffff';
    ctx.globalAlpha = 0.18 + state.emphasis * 0.4;
    ctx.arc(point.x, point.y, Math.max(0.6, radius * 0.32), 0, Math.PI * 2);
    ctx.fill();

    ctx.shadowBlur = 0;

    const labelX = point.x + 10;
    const labelY = point.y - 6;
    ctx.font = state.active ? '500 13px "Noto Sans JP", sans-serif' : state.related ? '400 12px "Noto Sans JP", sans-serif' : '400 11px "Noto Sans JP", sans-serif';
    ctx.fillStyle = state.active ? palette.activeText : palette.label;
    ctx.globalAlpha = state.active ? 0.96 : state.related ? 0.76 : Math.max(0.22, state.emphasis);
    ctx.fillText(node.label, labelX, labelY);

    if (state.active && node.subtitle) {
      ctx.font = '400 10px "DM Mono", monospace';
      ctx.fillStyle = 'rgba(238, 230, 216, 0.54)';
      ctx.globalAlpha = 0.9;
      ctx.fillText(node.subtitle, labelX, labelY + 15);
    }
  }

  function drawNodes() {
    for (const node of nodes) {
      drawNode(node, getNodeState(node));
    }
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
  }

  function frame() {
    updateFrameState();
    drawBackground();
    drawLinks();
    drawNodes();
    requestAnimationFrame(frame);
  }

  canvas.addEventListener('pointerdown', handlePointerDown);
  canvas.addEventListener('pointermove', handlePointerMove);
  canvas.addEventListener('pointerup', handlePointerUp);
  canvas.addEventListener('pointerleave', handlePointerLeave);
  window.addEventListener('resize', resize);

  runLayout(240);
  resize();
  updateFocusLabel();
  updateCursor();
  frame();
})();
