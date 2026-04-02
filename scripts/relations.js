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
    movement: '#9ec3f4',
    idea: '#d7c4f0',
    activeText: '#f5ecdf',
    text: 'rgba(238, 230, 216, 0.78)',
    textDim: 'rgba(238, 230, 216, 0.24)',
    link: 'rgba(211, 186, 151, 0.5)',
    linkGlow: 'rgba(211, 186, 151, 0.12)',
    guide: 'rgba(238, 230, 216, 0.07)',
    guideText: 'rgba(238, 230, 216, 0.2)',
    frame: 'rgba(198, 170, 130, 0.1)'
  };

  const typeLabel = {
    photographer: '写真家',
    movement: '運動',
    idea: '思想'
  };

  const state = {
    width: 0,
    height: 0,
    ratio: 1,
    scale: 1,
    targetScale: 1,
    overviewScale: 1,
    focusScale: 1,
    cameraX: 0,
    cameraY: 0,
    targetCameraX: 0,
    targetCameraY: 0,
    cameraLockedToFocus: false,
    pointerX: 0,
    pointerY: 0,
    pointerDown: false,
    dragging: false,
    dragPointerId: null,
    dragStartX: 0,
    dragStartY: 0,
    dragStartCameraX: 0,
    dragStartCameraY: 0,
    pressedNodeId: '',
    hoveredNodeId: '',
    focusedNodeId: '',
    adjacency: new Map(),
    nodesById: new Map(),
    stars: [],
    world: {
      minX: -2200,
      maxX: 2200,
      minY: -1300,
      maxY: 1500
    }
  };

  const nodes = RELATION_GRAPH.nodes.map(node => ({
    ...node,
    x: 0,
    y: 0,
    glow: 0,
    hitWidth: Math.max(90, node.label.length * 16 + 36)
  }));

  const links = RELATION_GRAPH.links.map(link => ({
    ...link,
    sourceNode: null,
    targetNode: null
  }));

  nodes.forEach(node => {
    state.nodesById.set(node.id, node);
    state.adjacency.set(node.id, new Set());
  });

  links.forEach(link => {
    link.sourceNode = state.nodesById.get(link.source);
    link.targetNode = state.nodesById.get(link.target);
    if (!link.sourceNode || !link.targetNode) return;
    state.adjacency.get(link.source).add(link.target);
    state.adjacency.get(link.target).add(link.source);
  });

  function createStars() {
    state.stars = Array.from(
      { length: Math.max(120, Math.round((state.width * state.height) / 16000)) },
      (_, index) => ({
        x: (index * 197.3) % state.width,
        y: (index * 113.7) % state.height,
        radius: ((index * 17) % 10) / 10 + 0.4,
        alpha: (((index * 23) % 10) / 10) * 0.22 + 0.04
      })
    );
  }

  function resize() {
    state.ratio = window.devicePixelRatio || 1;
    state.width = window.innerWidth;
    state.height = window.innerHeight;
    canvas.width = state.width * state.ratio;
    canvas.height = state.height * state.ratio;
    canvas.style.width = `${state.width}px`;
    canvas.style.height = `${state.height}px`;
    ctx.setTransform(state.ratio, 0, 0, state.ratio, 0, 0);
    createStars();
    updateScaleTargets();
  }

  function layoutNodes() {
    const photographers = nodes.filter(node => node.type === 'photographer');
    const movements = nodes.filter(node => node.type === 'movement');
    const ideas = nodes.filter(node => node.type === 'idea');
    const eraOrder = RELATION_GRAPH.eras.map(era => era.id);

    const eraSpacing = 520;
    const startX = -((eraOrder.length - 1) * eraSpacing) / 2;
    const photographerByEra = new Map();

    photographers.forEach(node => {
      const list = photographerByEra.get(node.era) || [];
      list.push(node);
      photographerByEra.set(node.era, list);
    });

    eraOrder.forEach((eraId, eraIndex) => {
      const eraNodes = photographerByEra.get(eraId) || [];
      const columns = Math.max(1, Math.ceil(eraNodes.length / 5));
      eraNodes.forEach((node, index) => {
        const column = Math.floor(index / 5);
        const row = index % 5;
        node.x = startX + eraIndex * eraSpacing + (column - (columns - 1) / 2) * 120;
        node.y = -120 + row * 180 + ((index + eraIndex) % 2 === 0 ? -24 : 24);
      });
    });

    const movementUsage = new Map();
    movements.forEach(node => {
      const relatedPhotographers = links
        .filter(link => link.type === 'belongs_to' && (link.source === node.id || link.target === node.id))
        .map(link => (link.source === node.id ? link.targetNode : link.sourceNode))
        .filter(Boolean);
      const avgX = relatedPhotographers.length
        ? relatedPhotographers.reduce((sum, item) => sum + item.x, 0) / relatedPhotographers.length
        : 0;
      movementUsage.set(node.id, avgX);
    });

    const sortedMovements = [...movements].sort((a, b) => movementUsage.get(a.id) - movementUsage.get(b.id));
    sortedMovements.forEach((node, index) => {
      const row = index % 4;
      node.x = movementUsage.get(node.id) + (row - 1.5) * 70;
      node.y = -860 + row * 110;
    });

    const ideaUsage = new Map();
    ideas.forEach(node => {
      const relatedMovements = links
        .filter(link => link.type === 'idea' && (link.source === node.id || link.target === node.id))
        .map(link => (link.source === node.id ? link.targetNode : link.sourceNode))
        .filter(Boolean);
      const avgX = relatedMovements.length
        ? relatedMovements.reduce((sum, item) => sum + item.x, 0) / relatedMovements.length
        : 0;
      ideaUsage.set(node.id, avgX);
    });

    const sortedIdeas = [...ideas].sort((a, b) => ideaUsage.get(a.id) - ideaUsage.get(b.id));
    sortedIdeas.forEach((node, index) => {
      const row = index % 3;
      node.x = ideaUsage.get(node.id) + (row - 1) * 120;
      node.y = 1040 + row * 120;
    });

    const allX = nodes.map(node => node.x);
    const allY = nodes.map(node => node.y);
    state.world.minX = Math.min(...allX) - 620;
    state.world.maxX = Math.max(...allX) + 620;
    state.world.minY = Math.min(...allY) - 420;
    state.world.maxY = Math.max(...allY) + 420;
    state.cameraX = (state.world.minX + state.world.maxX) * 0.5;
    state.targetCameraX = state.cameraX;
    state.cameraY = (state.world.minY + state.world.maxY) * 0.5;
    state.targetCameraY = state.cameraY;
    updateScaleTargets();
  }

  function updateScaleTargets() {
    const worldWidth = Math.max(1, state.world.maxX - state.world.minX);
    const worldHeight = Math.max(1, state.world.maxY - state.world.minY);
    const fitX = (state.width * 0.82) / worldWidth;
    const fitY = (state.height * 0.72) / worldHeight;
    state.overviewScale = Math.max(0.14, Math.min(0.34, fitX, fitY));
    state.focusScale = Math.max(0.42, Math.min(0.72, state.overviewScale * 2.1));

    if (!state.scale || state.scale === 1) {
      state.scale = state.overviewScale;
      state.targetScale = state.overviewScale;
      return;
    }

    state.targetScale = state.focusedNodeId ? state.focusScale : state.overviewScale;
  }

  function worldToScreen(x, y) {
    return {
      x: state.width * 0.5 + (x - state.cameraX) * state.scale,
      y: state.height * 0.5 + (y - state.cameraY) * state.scale
    };
  }

  function clampCamera() {
    const halfViewX = state.width / (2 * state.targetScale);
    const halfViewY = state.height / (2 * state.targetScale);
    const minX = state.world.minX + halfViewX;
    const maxX = state.world.maxX - halfViewX;
    const minY = state.world.minY + halfViewY;
    const maxY = state.world.maxY - halfViewY;

    state.targetCameraX = minX > maxX
      ? (state.world.minX + state.world.maxX) * 0.5
      : Math.max(minX, Math.min(maxX, state.targetCameraX));
    state.targetCameraY = minY > maxY
      ? (state.world.minY + state.world.maxY) * 0.5
      : Math.max(minY, Math.min(maxY, state.targetCameraY));
  }

  function getFocusedNode() {
    return state.focusedNodeId ? state.nodesById.get(state.focusedNodeId) : null;
  }

  function getHoveredNode() {
    return state.hoveredNodeId ? state.nodesById.get(state.hoveredNodeId) : null;
  }

  function setFocusedNode(id) {
    if (!id || !state.nodesById.has(id)) return;
    state.focusedNodeId = id;
    state.cameraLockedToFocus = true;
    const node = state.nodesById.get(id);
    state.targetCameraX = node.x;
    state.targetCameraY = node.y;
    state.targetScale = state.focusScale;
    node.glow = 1.4;
    clampCamera();
    updateFocusPanel();
  }

  function updateFocusPanel() {
    const node = getFocusedNode();
    const hovered = getHoveredNode();
    const target = node || hovered;

    if (!target) {
      labelEl.textContent = '関係の星図';
      metaEl.textContent = '点ではなく名前そのものをたどりながら、関係の地図を横断します。';
      hintEl.textContent = prefersCoarse
        ? 'タップで中心に寄せ、同じ名前をもう一度タップで詳細へ。'
        : 'クリックで中心に寄せ、同じ名前をもう一度クリックで詳細へ。';
      return;
    }

    const relatedCount = state.adjacency.get(target.id)?.size || 0;
    labelEl.textContent = target.label;
    metaEl.textContent = `${typeLabel[target.type]} / ${relatedCount}つの接続${target.subtitle ? ` / ${target.subtitle}` : ''}`;
    if (node && node.id === target.id) {
      hintEl.textContent = target.url
        ? '固定中。もう一度クリックすると詳細ページへ移動します。'
        : '固定中。ドラッグで地図を移動できます。';
    } else {
      hintEl.textContent = 'まだ固定されていません。クリックするとこの名前が中心になります。';
    }
  }

  function findNodeAt(x, y) {
    let best = null;
    let bestScore = Infinity;

    for (const node of nodes) {
      const point = worldToScreen(node.x, node.y);
      const labelLeft = point.x - 10;
      const labelTop = point.y - 18;
      const labelRight = labelLeft + node.hitWidth;
      const labelBottom = labelTop + 28;
      const inLabel = x >= labelLeft && x <= labelRight && y >= labelTop && y <= labelBottom;
      const dx = point.x - x;
      const dy = point.y - y;
      const inCore = Math.hypot(dx, dy) <= 18;
      if (!inLabel && !inCore) continue;

      const score = inLabel
        ? Math.hypot(x - (labelLeft + labelRight) * 0.5, y - (labelTop + labelBottom) * 0.5)
        : Math.hypot(dx, dy);

      if (score < bestScore) {
        best = node;
        bestScore = score;
      }
    }

    return best;
  }

  function updateCursor() {
    if (state.dragging) {
      canvas.style.cursor = 'grabbing';
      return;
    }
    canvas.style.cursor = findNodeAt(state.pointerX, state.pointerY) ? 'pointer' : 'grab';
  }

  function navigateTo(node) {
    if (!node.url) return;
    node.glow = 2;
    document.body.classList.add('is-navigating');
    fadeEl.addEventListener('transitionend', () => {
      window.location.href = node.url;
    }, { once: true });
  }

  function handlePointerDown(event) {
    canvas.setPointerCapture(event.pointerId);
    state.pointerDown = true;
    state.dragging = false;
    state.dragPointerId = event.pointerId;
    state.dragStartX = event.clientX;
    state.dragStartY = event.clientY;
    state.dragStartCameraX = state.targetCameraX;
    state.dragStartCameraY = state.targetCameraY;
    state.pointerX = event.clientX;
    state.pointerY = event.clientY;
    const node = findNodeAt(event.clientX, event.clientY);
    state.pressedNodeId = node ? node.id : '';
    updateCursor();
  }

  function handlePointerMove(event) {
    state.pointerX = event.clientX;
    state.pointerY = event.clientY;

    if (state.pointerDown && state.dragPointerId === event.pointerId) {
      const dx = event.clientX - state.dragStartX;
      const dy = event.clientY - state.dragStartY;
      if (!state.dragging && Math.hypot(dx, dy) > 8) {
        state.dragging = true;
        state.cameraLockedToFocus = false;
      }
      if (state.dragging) {
        state.targetCameraX = state.dragStartCameraX - (dx / state.scale);
        state.targetCameraY = state.dragStartCameraY - (dy / state.scale);
        clampCamera();
        updateCursor();
        return;
      }
    }

    const nextHovered = findNodeAt(event.clientX, event.clientY);
    const nextId = nextHovered ? nextHovered.id : '';
    if (state.hoveredNodeId !== nextId) {
      state.hoveredNodeId = nextId;
      updateFocusPanel();
    }
    updateCursor();
  }

  function handlePointerLeave() {
    state.hoveredNodeId = '';
    updateFocusPanel();
    updateCursor();
  }

  function handlePointerUp(event) {
    if (canvas.hasPointerCapture(event.pointerId)) {
      canvas.releasePointerCapture(event.pointerId);
    }

    const wasDragging = state.dragging;
    state.pointerDown = false;
    state.dragPointerId = null;
    state.dragging = false;

    if (wasDragging) {
      updateCursor();
      return;
    }

    const node = findNodeAt(event.clientX, event.clientY);
    if (!node || node.id !== state.pressedNodeId) {
      state.pressedNodeId = '';
      updateCursor();
      return;
    }

    if (state.focusedNodeId === node.id && node.url) {
      navigateTo(node);
    } else {
      setFocusedNode(node.id);
    }

    state.pressedNodeId = '';
    updateCursor();
  }

  function getNodeState(node) {
    const focused = getFocusedNode();
    const hovered = getHoveredNode();
    const relatedIds = focused ? state.adjacency.get(focused.id) : null;

    if (focused) {
      if (node.id === focused.id) {
        return { emphasis: 1, active: true, related: false, hovered: false };
      }
      if (relatedIds?.has(node.id)) {
        return { emphasis: 0.66, active: false, related: true, hovered: false };
      }
      if (hovered && node.id === hovered.id) {
        return { emphasis: 0.28, active: false, related: false, hovered: true };
      }
      return { emphasis: 0.1, active: false, related: false, hovered: false };
    }

    if (hovered && node.id === hovered.id) {
      return { emphasis: 0.8, active: false, related: false, hovered: true };
    }

    return { emphasis: 0.38, active: false, related: false, hovered: false };
  }

  function updateFrameState() {
    if (!state.focusedNodeId) {
      state.targetScale = state.overviewScale;
    }
    clampCamera();
    state.scale += (state.targetScale - state.scale) * 0.08;
    state.cameraX += (state.targetCameraX - state.cameraX) * 0.08;
    state.cameraY += (state.targetCameraY - state.cameraY) * 0.08;

    nodes.forEach(node => {
      node.glow *= 0.88;
    });
  }

  function drawBackground() {
    ctx.clearRect(0, 0, state.width, state.height);

    const gradient = ctx.createRadialGradient(
      state.width * 0.52,
      state.height * 0.42,
      0,
      state.width * 0.52,
      state.height * 0.42,
      state.width * 0.78
    );
    gradient.addColorStop(0, 'rgba(15, 18, 24, 0.82)');
    gradient.addColorStop(1, 'rgba(4, 5, 8, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, state.width, state.height);

    state.stars.forEach(star => {
      ctx.beginPath();
      ctx.fillStyle = `rgba(255, 247, 235, ${star.alpha})`;
      ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
      ctx.fill();
    });
  }

  function drawWorldGuides() {
    ctx.save();
    ctx.strokeStyle = palette.guide;
    ctx.lineWidth = 1;

    for (let x = Math.ceil(state.world.minX / 240) * 240; x <= state.world.maxX; x += 240) {
      const start = worldToScreen(x, state.world.minY);
      const end = worldToScreen(x, state.world.maxY);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.stroke();
    }

    for (let y = Math.ceil(state.world.minY / 220) * 220; y <= state.world.maxY; y += 220) {
      const start = worldToScreen(state.world.minX, y);
      const end = worldToScreen(state.world.maxX, y);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.stroke();
    }

    ctx.strokeStyle = palette.frame;
    const topLeft = worldToScreen(state.world.minX, state.world.minY);
    const bottomRight = worldToScreen(state.world.maxX, state.world.maxY);
    ctx.strokeRect(
      topLeft.x,
      topLeft.y,
      bottomRight.x - topLeft.x,
      bottomRight.y - topLeft.y
    );

    ctx.font = '400 10px "DM Mono", monospace';
    ctx.fillStyle = palette.guideText;
    RELATION_GRAPH.eras.forEach((era, index) => {
      const x = -((RELATION_GRAPH.eras.length - 1) * 520) / 2 + index * 520;
      const point = worldToScreen(x, -1060);
      ctx.fillText(era.label, point.x - 24, point.y);
    });

    ctx.fillText('運動', worldToScreen(state.world.minX + 120, -990).x, worldToScreen(state.world.minX + 120, -990).y);
    ctx.fillText('写真家', worldToScreen(state.world.minX + 120, -40).x, worldToScreen(state.world.minX + 120, -40).y);
    ctx.fillText('思想', worldToScreen(state.world.minX + 120, 980).x, worldToScreen(state.world.minX + 120, 980).y);
    ctx.restore();
  }

  function drawLinks() {
    const focused = getFocusedNode();
    if (!focused) return;

    links.forEach(link => {
      const active = link.source === focused.id || link.target === focused.id;
      if (!active || !link.sourceNode || !link.targetNode) return;
      const start = worldToScreen(link.sourceNode.x, link.sourceNode.y);
      const end = worldToScreen(link.targetNode.x, link.targetNode.y);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.strokeStyle = palette.link;
      ctx.lineWidth = link.type === 'idea' ? 0.8 : 1;
      ctx.globalAlpha = link.type === 'era' ? 0.34 : 0.88;
      ctx.shadowBlur = 8;
      ctx.shadowColor = palette.linkGlow;
      ctx.stroke();
      ctx.shadowBlur = 0;
    });

    ctx.globalAlpha = 1;
  }

  function drawNode(node, nodeState) {
    const point = worldToScreen(node.x, node.y);
    const baseRadius = node.type === 'photographer' ? 1.7 : node.type === 'movement' ? 1.5 : 1.3;
    const radius = baseRadius + (nodeState.active ? 3.2 : nodeState.related ? 1.6 : nodeState.hovered ? 1 : 0) + node.glow;

    ctx.beginPath();
    ctx.fillStyle = palette[node.type];
    ctx.globalAlpha = 0.14 + nodeState.emphasis * 0.82;
    ctx.shadowBlur = 8 + nodeState.emphasis * 14;
    ctx.shadowColor = palette[node.type];
    ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.fillStyle = '#ffffff';
    ctx.globalAlpha = 0.08 + nodeState.emphasis * 0.36;
    ctx.arc(point.x, point.y, Math.max(0.6, radius * 0.34), 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    const labelX = point.x + 11;
    const labelY = point.y - 4;
    ctx.font = nodeState.active
      ? '500 13px "Noto Sans JP", sans-serif'
      : nodeState.related
        ? '400 12px "Noto Sans JP", sans-serif'
        : '400 10px "Noto Sans JP", sans-serif';
    ctx.fillStyle = nodeState.active ? palette.activeText : palette.text;
    ctx.globalAlpha = nodeState.active ? 0.98 : nodeState.related ? 0.82 : Math.max(0.24, nodeState.emphasis);
    ctx.fillText(node.label, labelX, labelY);

    if ((nodeState.active || nodeState.hovered) && node.subtitle) {
      ctx.font = '400 10px "DM Mono", monospace';
      ctx.fillStyle = 'rgba(238, 230, 216, 0.5)';
      ctx.globalAlpha = nodeState.active ? 0.86 : 0.52;
      ctx.fillText(node.subtitle, labelX, labelY + 15);
    }
  }

  function drawNodes() {
    nodes.forEach(node => {
      drawNode(node, getNodeState(node));
    });
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
  }

  function frame() {
    updateFrameState();
    drawBackground();
    drawWorldGuides();
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
  layoutNodes();
  updateFocusPanel();
  updateCursor();
  frame();
})();
