(function () {
  const canvas = document.getElementById('constellation-canvas');
  const ctx = canvas.getContext('2d');
  const labelEl = document.getElementById('focus-label');
  const metaEl = document.getElementById('focus-meta');
  const hintEl = document.getElementById('focus-hint');
  const fadeEl = document.getElementById('page-fade');
  const prefersCoarse = window.matchMedia('(pointer: coarse)').matches;

  const palette = {
    photographer: '#f0dbc0',
    movement: '#9ec5ff',
    idea: '#c9b8ff',
    link: 'rgba(194, 170, 132, 0.55)',
    inactiveLink: 'rgba(194, 170, 132, 0.08)',
    text: '#efe6d8',
    dim: 'rgba(239, 230, 216, 0.42)'
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
    hoverNodeId: '',
    selectedNodeId: '',
    pressedNodeId: '',
    focusedNodeId: '',
    adjacency: new Map(),
    nodesById: new Map(),
    stars: []
  };

  const nodes = RELATION_GRAPH.nodes.map((node, index) => {
    const angle = (Math.PI * 2 * index) / RELATION_GRAPH.nodes.length;
    const radius = 160 + (index % 5) * 40;
    return {
      ...node,
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      vx: 0,
      vy: 0,
      radius: node.type === 'photographer' ? 2.4 : node.type === 'movement' ? 2.1 : 1.9,
      glow: 0
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
    simulation.scale = Math.min(simulation.width, simulation.height) / 900;
    createStars();
  }

  function createStars() {
    simulation.stars = Array.from({ length: Math.max(120, Math.round((simulation.width * simulation.height) / 14000)) }, () => ({
      x: Math.random() * simulation.width,
      y: Math.random() * simulation.height,
      radius: Math.random() * 1.3 + 0.2,
      alpha: Math.random() * 0.4 + 0.08
    }));
  }

  function getFocusedNode() {
    const focusId = simulation.hoverNodeId || simulation.selectedNodeId;
    simulation.focusedNodeId = focusId;
    return focusId ? simulation.nodesById.get(focusId) : null;
  }

  function worldToScreen(x, y) {
    return {
      x: simulation.width * 0.5 + (x - simulation.cameraX),
      y: simulation.height * 0.5 + (y - simulation.cameraY)
    };
  }

  function findNodeAt(x, y) {
    let best = null;
    let minDistance = Infinity;
    for (const node of nodes) {
      const point = worldToScreen(node.x, node.y);
      const dx = point.x - x;
      const dy = point.y - y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const threshold = Math.max(14, node.radius * 4.8);
      if (distance < threshold && distance < minDistance) {
        best = node;
        minDistance = distance;
      }
    }
    return best;
  }

  function updateFocusLabel() {
    const node = getFocusedNode();
    if (!node) {
      labelEl.textContent = 'Hover to trace influence';
      metaEl.textContent = 'Tap on mobile to hold a constellation.';
      hintEl.textContent = 'Click a node to move deeper into the archive.';
      return;
    }

    const relatedCount = simulation.adjacency.get(node.id).size;
    labelEl.textContent = node.id;
    metaEl.textContent = `${capitalize(node.type)} · ${relatedCount} connection${relatedCount === 1 ? '' : 's'}`;
    hintEl.textContent = prefersCoarse
      ? 'Tap again to move to the linked page.'
      : 'Click to move to the linked page.';
  }

  function capitalize(value) {
    return value.charAt(0).toUpperCase() + value.slice(1);
  }

  function updateCursor() {
    if (simulation.dragging) {
      canvas.style.cursor = 'grabbing';
      return;
    }
    const node = findNodeAt(simulation.pointerX, simulation.pointerY);
    canvas.style.cursor = node && node.url ? 'pointer' : 'grab';
  }

  function updateInteractionFocus(clientX, clientY) {
    simulation.pointerX = clientX;
    simulation.pointerY = clientY;
    if (!prefersCoarse) {
      const node = findNodeAt(clientX, clientY);
      simulation.hoverNodeId = node ? node.id : '';
      updateFocusLabel();
      updateCursor();
    }
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
      if (!simulation.dragging && Math.sqrt(dx * dx + dy * dy) > 8) {
        simulation.dragging = true;
      }
      if (simulation.dragging) {
        simulation.hoverNodeId = '';
        simulation.targetCameraX = simulation.dragStartCameraX - dx;
        simulation.targetCameraY = simulation.dragStartCameraY - dy;
        updateFocusLabel();
      }
    }

    if (!simulation.dragging) {
      updateInteractionFocus(event.clientX, event.clientY);
    } else {
      updateCursor();
    }
  }

  function handlePointerLeave() {
    if (!prefersCoarse && !simulation.pointerDown) {
      simulation.hoverNodeId = '';
      updateFocusLabel();
      updateCursor();
    }
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
      if (simulation.selectedNodeId === node.id && node.url) {
        navigateTo(node);
      } else {
        simulation.selectedNodeId = node.id;
        updateFocusLabel();
      }
    } else if (node.url) {
      navigateTo(node);
    }

    simulation.pressedNodeId = '';
    updateCursor();
  }

  function navigateTo(node) {
    node.glow = 1.6;
    document.body.classList.add('is-navigating');
    fadeEl.addEventListener('transitionend', () => {
      window.location.href = node.url;
    }, { once: true });
  }

  function getNodeState(node) {
    const focused = getFocusedNode();
    const relatedIds = focused ? simulation.adjacency.get(focused.id) : null;
    if (!focused) {
      return { emphasis: 0.42, active: false, related: false };
    }
    if (focused.id === node.id) {
      return { emphasis: 1, active: true, related: false };
    }
    if (relatedIds.has(node.id)) {
      return { emphasis: 0.72, active: false, related: true };
    }
    return { emphasis: 0.1, active: false, related: false };
  }

  function simulate() {
    const centering = 0.0009 * simulation.scale;
    const repulsion = 6800 * simulation.scale;
    const spring = 0.0016 * simulation.scale;

    for (let i = 0; i < nodes.length; i += 1) {
      const a = nodes[i];
      for (let j = i + 1; j < nodes.length; j += 1) {
        const b = nodes[j];
        let dx = b.x - a.x;
        let dy = b.y - a.y;
        let distanceSq = dx * dx + dy * dy;
        if (distanceSq < 0.01) {
          dx = (Math.random() - 0.5) * 0.1;
          dy = (Math.random() - 0.5) * 0.1;
          distanceSq = dx * dx + dy * dy;
        }
        const force = repulsion / distanceSq;
        const distance = Math.sqrt(distanceSq);
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
      const desired = link.sourceNode.type === 'movement' || link.targetNode.type === 'movement' ? 190 : 150;
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
      node.vx *= 0.93;
      node.vy *= 0.93;
      node.x += node.vx;
      node.y += node.vy;
      node.glow *= 0.92;
    }

    const focused = getFocusedNode();
    if (!simulation.pointerDown || !simulation.dragging) {
      simulation.targetCameraX = focused ? focused.x : simulation.targetCameraX * 0.96;
      simulation.targetCameraY = focused ? focused.y : simulation.targetCameraY * 0.96;
    }
    simulation.cameraX += (simulation.targetCameraX - simulation.cameraX) * 0.08;
    simulation.cameraY += (simulation.targetCameraY - simulation.cameraY) * 0.08;
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
    gradient.addColorStop(0, 'rgba(18, 20, 28, 0.68)');
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
    const activeIds = focused ? simulation.adjacency.get(focused.id) : null;

    for (const link of links) {
      const sourceState = getNodeState(link.sourceNode);
      const targetState = getNodeState(link.targetNode);
      const active = focused && (
        link.source === focused.id ||
        link.target === focused.id ||
        (activeIds.has(link.source) && link.target === focused.id) ||
        (activeIds.has(link.target) && link.source === focused.id)
      );

      const start = worldToScreen(link.sourceNode.x, link.sourceNode.y);
      const end = worldToScreen(link.targetNode.x, link.targetNode.y);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.strokeStyle = active ? palette.link : palette.inactiveLink;
      ctx.lineWidth = active ? 0.9 : 0.55;
      ctx.globalAlpha = focused ? Math.max(sourceState.emphasis, targetState.emphasis) : 0.24;
      ctx.shadowBlur = active ? 14 : 0;
      ctx.shadowColor = active ? 'rgba(201, 184, 255, 0.28)' : 'transparent';
      ctx.stroke();
      ctx.globalAlpha = 1;
      ctx.shadowBlur = 0;
    }
  }

  function drawNodes() {
    for (const node of nodes) {
      const state = getNodeState(node);
      const point = worldToScreen(node.x, node.y);
      const radius = node.radius + (state.active ? 3.6 : state.related ? 1.9 : 0) + node.glow;

      ctx.beginPath();
      ctx.fillStyle = palette[node.type];
      ctx.globalAlpha = 0.22 + state.emphasis * 0.78;
      ctx.shadowBlur = 18 + state.emphasis * 20 + node.glow * 16;
      ctx.shadowColor = palette[node.type];
      ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
      ctx.fill();

      ctx.beginPath();
      ctx.fillStyle = '#ffffff';
      ctx.globalAlpha = 0.18 + state.emphasis * 0.64;
      ctx.arc(point.x, point.y, Math.max(0.8, radius * 0.34), 0, Math.PI * 2);
      ctx.fill();

      if (state.active || state.related) {
        ctx.font = state.active ? '500 13px "DM Mono", monospace' : '400 11px "DM Mono", monospace';
        ctx.fillStyle = palette.text;
        ctx.globalAlpha = state.active ? 0.92 : 0.58;
        ctx.shadowBlur = 0;
        ctx.fillText(node.id, point.x + 12, point.y - 10);
      }
    }

    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
  }

  function frame() {
    simulate();
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

  resize();
  updateFocusLabel();
  updateCursor();
  frame();
})();
