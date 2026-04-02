(function () {
  const canvas = document.getElementById('constellation-canvas');
  const ctx = canvas.getContext('2d');
  const labelEl = document.getElementById('focus-label');
  const metaEl = document.getElementById('focus-meta');
  const hintEl = document.getElementById('focus-hint');
  const fadeEl = document.getElementById('page-fade');
  const zoomInButton = document.getElementById('zoom-in');
  const zoomOutButton = document.getElementById('zoom-out');
  const resetViewButton = document.getElementById('reset-view');
  const prefersCoarse = window.matchMedia('(pointer: coarse)').matches;

  const palette = {
    photographer: '#f1ddc1',
    movement: '#9ec3f4',
    idea: '#d7c4f0',
    activeText: '#f5ecdf',
    text: 'rgba(238, 230, 216, 0.78)',
    textOutline: '#040507',
    link: 'rgba(211, 186, 151, 0.5)',
    linkGlow: 'rgba(211, 186, 151, 0.12)',
    focusLinkDepth1: 'rgba(126, 212, 255, 0.92)',
    focusLinkDepth1Glow: 'rgba(126, 212, 255, 0.24)',
    focusLinkDepth2: 'rgba(227, 198, 149, 0.7)',
    focusLinkDepth2Glow: 'rgba(227, 198, 149, 0.16)'
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
    defaultScale: 0.5,
    minScale: 0.3,
    maxScale: 1.15,
    cameraX: 0,
    cameraY: 0,
    targetCameraX: 0,
    targetCameraY: 0,
    focusAnchorX: 0,
    focusAnchorY: 0,
    stageAnchorX: 0,
    stageAnchorY: 0,
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
    initialNodeId: '',
    ambientMotionUntil: 0,
    frameHandle: 0,
    focusClusterCache: null,
    focusTraversalCache: null,
    focusLayoutCache: null,
    maxVisibleDepth: 2,
    adjacency: new Map(),
    neighborEdges: new Map(),
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
    homeX: 0,
    homeY: 0,
    glow: 0,
    hitWidth: Math.max(90, node.label.length * 16 + 36)
  }));

  const links = RELATION_GRAPH.links.map(link => ({
    ...link,
    sourceNode: null,
    targetNode: null
  }));

  function hashNumber(value) {
    let hash = 0;
    for (let i = 0; i < value.length; i += 1) {
      hash = ((hash << 5) - hash) + value.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash);
  }

  function jitter(value, amplitude) {
    return ((hashNumber(value) % 1000) / 999 - 0.5) * amplitude;
  }

  function stableAngle(value) {
    return (hashNumber(value) % 360) * (Math.PI / 180);
  }

  function stableSortValue(value) {
    return hashNumber(value) % 100000;
  }

  function angleFromHome(focused, node) {
    const dx = node.homeX - focused.homeX;
    const dy = node.homeY - focused.homeY;
    if (Math.abs(dx) < 0.001 && Math.abs(dy) < 0.001) {
      return stableAngle(`${focused.id}:${node.id}`);
    }
    return Math.atan2(dy, dx);
  }

  function relaxHorizontally(list, minGap, iterations) {
    const ordered = [...list].sort((a, b) => a.x - b.x);
    for (let step = 0; step < iterations; step += 1) {
      for (let index = 1; index < ordered.length; index += 1) {
        const left = ordered[index - 1];
        const right = ordered[index];
        const gap = right.x - left.x;
        if (gap >= minGap) continue;
        const push = (minGap - gap) * 0.5;
        left.x -= push;
        right.x += push;
      }
    }
  }

  nodes.forEach(node => {
    state.nodesById.set(node.id, node);
    state.adjacency.set(node.id, new Set());
    state.neighborEdges.set(node.id, []);
  });

  links.forEach(link => {
    link.sourceNode = state.nodesById.get(link.source);
    link.targetNode = state.nodesById.get(link.target);
    if (!link.sourceNode || !link.targetNode) return;
    state.adjacency.get(link.source).add(link.target);
    state.adjacency.get(link.target).add(link.source);
    state.neighborEdges.get(link.source).push({ id: link.target, type: link.type });
    state.neighborEdges.get(link.target).push({ id: link.source, type: link.type });
  });

  function createStars() {
    const now = typeof performance !== 'undefined' && performance.now
      ? performance.now()
      : Date.now();
    state.ambientMotionUntil = now + 1100;
    state.stars = Array.from(
      { length: Math.max(260, Math.round((state.width * state.height) / 8200)) },
      (_, index) => ({
        x: (index * 197.3) % state.width,
        y: (index * 113.7) % state.height,
        radius: ((index * 17) % 10) / 10 + 0.5,
        alpha: (((index * 23) % 10) / 10) * 0.34 + 0.1,
        phase: ((index * 29) % 360) * (Math.PI / 180),
        driftX: (((index * 19) % 10) / 10 - 0.5) * 4.8,
        driftY: (((index * 31) % 10) / 10 - 0.5) * 4.1,
        pulse: (((index * 13) % 10) / 10) * 0.2 + 0.9,
        glow: ((index * 7) % 10) > 5 ? 1 : 0
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
    updateScaleBounds();
    const focused = getFocusedNode();
    if (focused) {
      frameFocusedViewport(focused);
    }
    scheduleFrame();
  }

  function layoutNodes() {
    const photographers = nodes.filter(node => node.type === 'photographer');
    const movements = nodes.filter(node => node.type === 'movement');
    const ideas = nodes.filter(node => node.type === 'idea');
    const eraOrder = RELATION_GRAPH.eras.map(era => era.id);

    const eraSpacing = 760;
    const startX = -((eraOrder.length - 1) * eraSpacing) / 2;
    const photographerByEra = new Map();

    photographers.forEach(node => {
      const list = photographerByEra.get(node.era) || [];
      list.push(node);
      photographerByEra.set(node.era, list);
    });

    eraOrder.forEach((eraId, eraIndex) => {
      const eraNodes = photographerByEra.get(eraId) || [];
      const columns = Math.max(1, Math.ceil(eraNodes.length / 4));
      eraNodes.forEach((node, index) => {
        const column = Math.floor(index / 4);
        const row = index % 4;
        node.x =
          startX +
          eraIndex * eraSpacing +
          (column - (columns - 1) / 2) * 220 +
          jitter(node.id, 90);
        node.y =
          -40 +
          row * 220 +
          jitter(`${node.id}:y`, 110);
      });

      relaxHorizontally(eraNodes, 150, 8);
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
      const row = index % 5;
      node.x = movementUsage.get(node.id) + jitter(node.id, 220);
      node.y = -860 + row * 155 + jitter(`${node.id}:y`, 40);
    });

    relaxHorizontally(sortedMovements, 170, 14);

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
      const row = index % 4;
      node.x = ideaUsage.get(node.id) + jitter(node.id, 260);
      node.y = 980 + row * 150 + jitter(`${node.id}:y`, 50);
    });

    relaxHorizontally(sortedIdeas, 180, 14);

    const allX = nodes.map(node => node.x);
    const allY = nodes.map(node => node.y);
    state.world.minX = Math.min(...allX) - 620;
    state.world.maxX = Math.max(...allX) + 620;
    state.world.minY = Math.min(...allY) - 420;
    state.world.maxY = Math.max(...allY) + 420;

    nodes.forEach(node => {
      node.homeX = node.x;
      node.homeY = node.y;
    });

    state.cameraX = (state.world.minX + state.world.maxX) * 0.5;
    state.targetCameraX = state.cameraX;
    state.cameraY = (state.world.minY + state.world.maxY) * 0.5;
    state.targetCameraY = state.cameraY;
    updateScaleBounds();
  }

  function updateScaleBounds() {
    const worldWidth = Math.max(1, state.world.maxX - state.world.minX);
    const worldHeight = Math.max(1, state.world.maxY - state.world.minY);
    const fitX = (state.width * 0.54) / worldWidth;
    const fitY = (state.height * 0.5) / worldHeight;
    const baseScale = Math.max(0.92, Math.min(1.7, fitX * 6.6, fitY * 6.6));
    state.defaultScale = baseScale;
    state.minScale = Math.max(0.38, baseScale * 0.45);
    state.maxScale = Math.max(3.6, baseScale * 3.8);

    if (!state.scale || state.scale === 1) {
      state.scale = state.defaultScale;
      state.targetScale = state.defaultScale;
      return;
    }

    state.scale = clampScale(state.scale);
    state.targetScale = clampScale(state.targetScale);
  }

  function clampScale(value) {
    return Math.max(state.minScale, Math.min(state.maxScale, value));
  }

  function getViewportInsets() {
    if (state.width < 900) {
      return {
        left: 26,
        right: 26,
        top: 120,
        bottom: 88
      };
    }

    return {
      left: Math.min(360, state.width * 0.29),
      right: 90,
      top: 122,
      bottom: 92
    };
  }

  function worldToScreen(x, y) {
    return {
      x: state.width * 0.5 + (x - state.cameraX) * state.scale,
      y: state.height * 0.5 + (y - state.cameraY) * state.scale
    };
  }

  function getDisplayTarget(node) {
    const focused = getFocusedNode();
    if (!focused) {
      state.focusClusterCache = null;
      state.focusTraversalCache = null;
      state.focusLayoutCache = null;
      return { x: node.homeX, y: node.homeY };
    }

    if (node.id === focused.id) {
      return { x: state.focusAnchorX, y: state.focusAnchorY };
    }

    const layoutMap = getFocusLayoutMap(focused);
    return layoutMap.get(node.id) || { x: node.homeX, y: node.homeY };
  }

  function getFocusClusterMap(focused) {
    if (state.focusClusterCache && state.focusClusterCache.focusId === focused.id) {
      return state.focusClusterCache.map;
    }

    const relatedIds = state.adjacency.get(focused.id);
    const map = new Map();
    if (!relatedIds || !relatedIds.size) {
      state.focusClusterCache = { focusId: focused.id, map };
      return map;
    }

    const relatedNodes = Array.from(relatedIds)
      .map(id => state.nodesById.get(id))
      .filter(Boolean)
      .sort((a, b) => {
        if (a.type !== b.type) return a.type.localeCompare(b.type, 'ja');
        return stableSortValue(`${focused.id}:${a.id}`) - stableSortValue(`${focused.id}:${b.id}`);
      });

    const total = relatedNodes.length;
    const ringCapacity = total > 14 ? 10 : 8;
    const baseRadius = 300 + Math.max(0, total - 4) * 26;

    relatedNodes.forEach((relatedNode, index) => {
      const ringIndex = Math.floor(index / ringCapacity);
      const slotsInRing = Math.min(ringCapacity, total - ringIndex * ringCapacity);
      const slot = index % ringCapacity;
      const typeOffset =
        relatedNode.type === 'photographer'
          ? 40
          : relatedNode.type === 'movement'
            ? 0
            : 90;
      const radius = baseRadius + ringIndex * 170 + typeOffset;
      const angleOffset = (stableAngle(`${focused.id}:${relatedNode.id}`) - Math.PI) * 0.08;
      const angle = -Math.PI / 2 + (slot / Math.max(1, slotsInRing)) * Math.PI * 2 + angleOffset;

      map.set(relatedNode.id, {
        x: focused.homeX + Math.cos(angle) * radius,
        y: focused.homeY + Math.sin(angle) * radius * 0.8
      });
    });

    state.focusClusterCache = { focusId: focused.id, map };
    return map;
  }

  function getFocusLayoutMap(focused) {
    if (state.focusLayoutCache && state.focusLayoutCache.focusId === focused.id) {
      return state.focusLayoutCache.map;
    }

    const traversal = getFocusTraversal(focused);
    const map = new Map();
    const childrenByParent = new Map();

    traversal.parents.forEach((parentId, nodeId) => {
      const depth = traversal.depths.get(nodeId);
      if (!parentId || depth > state.maxVisibleDepth) return;
      const node = state.nodesById.get(nodeId);
      if (!node) return;
      if (!childrenByParent.has(parentId)) childrenByParent.set(parentId, []);
      childrenByParent.get(parentId).push(node);
    });

    childrenByParent.forEach((children, parentId) => {
      const parentNode = state.nodesById.get(parentId) || focused;
      children.sort((a, b) => angleFromHome(parentNode, a) - angleFromHome(parentNode, b));
    });

    const rootChildren = childrenByParent.get(focused.id) || [];
    const rootCount = rootChildren.length;
    const rootRadius = 450 + Math.max(0, rootCount - 8) * 30;
    const rootStart = -Math.PI / 2;

    rootChildren.forEach((node, index) => {
      const angle = rootStart + (index / Math.max(1, rootCount)) * Math.PI * 2 + jitter(`${focused.id}:${node.id}:angle`, 0.16);
      const typeOffset =
        node.type === 'photographer'
          ? 0
          : node.type === 'movement'
            ? -24
            : 32;
      const radius = rootRadius + typeOffset + jitter(`${focused.id}:${node.id}:radius`, 14);
      map.set(node.id, {
        x: state.focusAnchorX + Math.cos(angle) * radius,
        y: state.focusAnchorY + Math.sin(angle) * radius * 0.84,
        angle
      });
    });

    rootChildren.forEach(parentNode => {
      const children = childrenByParent.get(parentNode.id) || [];
      if (!children.length) return;

      const parentPosition = map.get(parentNode.id);
      const baseAngle = parentPosition ? parentPosition.angle : angleFromHome(focused, parentNode);
      const span = Math.min(1.5, 0.64 + children.length * 0.18);
      const secondRadius = 820 + Math.max(0, children.length - 4) * 28;

      children.forEach((childNode, index) => {
        const spread = children.length === 1
          ? 0
          : ((index / (children.length - 1)) - 0.5) * span;
        const angle = baseAngle + spread + jitter(`${parentNode.id}:${childNode.id}:angle`, 0.1);
        const typeOffset =
          childNode.type === 'photographer'
            ? 0
            : childNode.type === 'movement'
              ? -34
              : 46;
        const radius = secondRadius + typeOffset + jitter(`${parentNode.id}:${childNode.id}:radius`, 18);
        map.set(childNode.id, {
          x: state.focusAnchorX + Math.cos(angle) * radius,
          y: state.focusAnchorY + Math.sin(angle) * radius * 0.86,
          angle
        });
      });
    });

    state.focusLayoutCache = { focusId: focused.id, map };
    return map;
  }

  function getFocusTraversal(focused) {
    if (state.focusTraversalCache && state.focusTraversalCache.focusId === focused.id) {
      return state.focusTraversalCache;
    }

    const depths = new Map([[focused.id, 0]]);
    const parents = new Map([[focused.id, null]]);
    const queue = [focused.id];

    for (let index = 0; index < queue.length; index += 1) {
      const currentId = queue[index];
      const currentDepth = depths.get(currentId);
      const currentNode = state.nodesById.get(currentId);
      const edges = getTraversalEdges(focused, currentNode, currentDepth);

      edges.forEach(({ id: nextId }) => {
        if (depths.has(nextId)) return;
        depths.set(nextId, currentDepth + 1);
        parents.set(nextId, currentId);
        queue.push(nextId);
      });
    }

    const traversal = {
      focusId: focused.id,
      depths,
      parents,
      maxDepth: Math.max(...depths.values())
    };

    state.focusTraversalCache = traversal;
    return traversal;
  }

  function getTraversalEdges(focused, currentNode, currentDepth) {
    if (!currentNode || currentDepth >= state.maxVisibleDepth) {
      return [];
    }

    const edges = (state.neighborEdges.get(currentNode.id) || [])
      .filter(edge => shouldTraverseEdge(focused, currentNode, edge));

    return prioritizeTraversalEdges(focused, currentNode, currentDepth, edges);
  }

  function shouldTraverseEdge(focused, currentNode, edge) {
    const nextNode = state.nodesById.get(edge.id);
    if (!nextNode || nextNode.id === focused.id) {
      return false;
    }

    if (currentNode.type === 'idea') {
      return false;
    }

    if (focused.type === 'photographer') {
      if (currentNode.id === focused.id) {
        return edge.type === 'movement_peer' || edge.type === 'era' || edge.type === 'belongs_to';
      }
      if (currentNode.type === 'movement') {
        return edge.type === 'belongs_to' || edge.type === 'influences' || edge.type === 'idea';
      }
      if (currentNode.type === 'photographer') {
        return edge.type === 'movement_peer' || edge.type === 'era';
      }
      return false;
    }

    if (focused.type === 'movement') {
      if (currentNode.type === 'movement') {
        return edge.type === 'influences' || edge.type === 'idea';
      }
      if (currentNode.type === 'photographer') {
        return edge.type === 'era';
      }
      return false;
    }

    if (focused.type === 'idea') {
      return currentNode.type === 'movement' && edge.type === 'influences';
    }

    return false;
  }

  function prioritizeTraversalEdges(focused, currentNode, currentDepth, edges) {
    const ranked = [...edges].sort((a, b) => {
      const scoreDiff = scoreTraversalEdge(focused, currentNode, b) - scoreTraversalEdge(focused, currentNode, a);
      if (scoreDiff !== 0) return scoreDiff;
      return stableSortValue(`${currentNode.id}:${a.id}`) - stableSortValue(`${currentNode.id}:${b.id}`);
    });

    const limit = currentDepth === 0
      ? focused.type === 'photographer' ? 6 : 7
      : currentNode.type === 'movement'
        ? 5
        : 4;

    return ranked.slice(0, limit);
  }

  function scoreTraversalEdge(focused, currentNode, edge) {
    const nextNode = state.nodesById.get(edge.id);
    if (!nextNode) return -999;

    let score = 0;

    if (focused.type === 'photographer') {
      if (currentNode.id === focused.id) {
        if (nextNode.type === 'photographer') score += 120;
        if (edge.type === 'movement_peer') score += 60;
        if (edge.type === 'era') score += 35;
        if (edge.type === 'belongs_to') score += 18;
      } else if (currentNode.type === 'movement') {
        if (nextNode.type === 'photographer') score += 100;
        if (edge.type === 'belongs_to') score += 55;
        if (edge.type === 'influences') score += 12;
        if (edge.type === 'idea') score += 6;
      } else if (currentNode.type === 'photographer') {
        if (nextNode.type === 'photographer') score += 90;
        if (edge.type === 'movement_peer') score += 50;
        if (edge.type === 'era') score += 24;
      }
    } else if (focused.type === 'movement') {
      if (nextNode.type === 'photographer') score += 70;
      if (edge.type === 'belongs_to') score += 40;
      if (edge.type === 'influences') score += 18;
      if (edge.type === 'idea') score += 8;
    } else {
      if (edge.type === 'influences') score += 18;
      if (edge.type === 'belongs_to') score += 8;
    }

    if (focused.type === 'photographer' && nextNode.type === 'photographer') {
      const eraDistance = Math.abs((nextNode.order || 0) - (focused.order || 0));
      score += Math.max(0, 18 - eraDistance * 0.2);
    }

    if (focused.type === 'photographer' && currentNode.type === 'movement' && nextNode.type === 'photographer') {
      const orderDistance = Math.abs((nextNode.order || 0) - (focused.order || 0));
      score += Math.max(0, 22 - orderDistance * 0.18);
    }

    return score;
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

  function getFocusBounds(focused) {
    const layoutMap = getFocusLayoutMap(focused);
    const traversal = getFocusTraversal(focused);
    let minX = state.focusAnchorX;
    let maxX = state.focusAnchorX;
    let minY = state.focusAnchorY;
    let maxY = state.focusAnchorY;

    traversal.depths.forEach((depth, nodeId) => {
      if (depth === 0 || depth > state.maxVisibleDepth) return;
      const node = state.nodesById.get(nodeId);
      if (!node) return;
      const target = layoutMap.get(nodeId);
      const x = target ? target.x : node.homeX;
      const y = target ? target.y : node.homeY;
      minX = Math.min(minX, x - 220);
      maxX = Math.max(maxX, x + 220);
      minY = Math.min(minY, y - 130);
      maxY = Math.max(maxY, y + 130);
    });

    return { minX, maxX, minY, maxY };
  }

  function frameFocusedViewport(focused) {
    const insets = getViewportInsets();
    const availableWidth = Math.max(240, state.width - insets.left - insets.right);
    const availableHeight = Math.max(220, state.height - insets.top - insets.bottom);
    const bounds = getFocusBounds(focused);
    const boundsWidth = Math.max(220, bounds.maxX - bounds.minX);
    const boundsHeight = Math.max(220, bounds.maxY - bounds.minY);
    const fitScale = clampScale(Math.min(
      availableWidth / boundsWidth,
      availableHeight / boundsHeight
    ) * 0.9);

    state.targetScale = fitScale;

    const desiredScreenX = insets.left + availableWidth * 0.5;
    const desiredScreenY = insets.top + availableHeight * 0.5;
    const boundsCenterX = (bounds.minX + bounds.maxX) * 0.5;
    const boundsCenterY = (bounds.minY + bounds.maxY) * 0.5;

    state.targetCameraX = boundsCenterX - ((desiredScreenX - state.width * 0.5) / state.targetScale);
    state.targetCameraY = boundsCenterY - ((desiredScreenY - state.height * 0.5) / state.targetScale);
    clampCamera();
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
    state.focusClusterCache = null;
    state.focusTraversalCache = null;
    state.focusLayoutCache = null;
    state.cameraLockedToFocus = true;
    const node = state.nodesById.get(id);
    state.focusAnchorX = state.stageAnchorX;
    state.focusAnchorY = state.stageAnchorY;
    node.glow = 1.4;
    frameFocusedViewport(node);
    updateFocusPanel();
    scheduleFrame();
  }

  function updateFocusPanel() {
    const node = getFocusedNode();
    const hovered = getHoveredNode();
    const target = node || hovered;

    if (!target) {
      labelEl.textContent = '写真の座標';
      metaEl.textContent = '点ではなく名前そのものをたどりながら、関係の地図を横断します。';
      hintEl.textContent = prefersCoarse
        ? 'タップで関係を開き、◎で初期表示に戻れます。'
        : 'クリックで関係を開き、◎で初期表示に戻れます。';
      return;
    }

    const relatedCount = state.adjacency.get(target.id)?.size || 0;
    const traversal = node && node.id === target.id ? getFocusTraversal(target) : null;
    const reachCount = traversal
      ? Array.from(traversal.depths.values()).filter(depth => depth > 0 && depth <= state.maxVisibleDepth).length
      : 0;
    labelEl.textContent = target.label;
    metaEl.textContent = `${typeLabel[target.type]} / 直接 ${relatedCount} / 表示中 ${reachCount}`;
    if (node && node.id === target.id) {
      hintEl.textContent = target.url
        ? '固定中。線はこの対象から辿れるつながりを示します。もう一度クリックで詳細へ。'
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
      const placeLeft = isLabelOnLeft(node);
      const labelLeft = placeLeft ? point.x - 10 - node.hitWidth : point.x - 10;
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

  function nudgeZoom(multiplier) {
    state.targetScale = clampScale(state.targetScale * multiplier);
    clampCamera();
    scheduleFrame();
  }

  function handleWheel(event) {
    event.preventDefault();
    const multiplier = Math.exp(-event.deltaY * 0.0022);
    state.targetScale = clampScale(state.targetScale * multiplier);
    clampCamera();
    scheduleFrame();
  }

  function isLabelOnLeft(node) {
    const focused = getFocusedNode();
    if (!focused) return false;
    return node.x < state.focusAnchorX;
  }

  function navigateTo(node) {
    if (!node.url) return;
    node.glow = 2;
    document.body.classList.add('is-navigating');
    scheduleFrame();
    fadeEl.addEventListener('transitionend', () => {
      window.location.href = node.url;
    }, { once: true });
  }

  function resetView() {
    const initialNode = state.nodesById.get(state.initialNodeId) || nodes.find(node => node.type === 'photographer') || nodes[0];
    if (!initialNode) return;

    state.focusedNodeId = '';
    state.hoveredNodeId = '';
    state.focusClusterCache = null;
    state.focusTraversalCache = null;
    state.focusLayoutCache = null;
    state.cameraLockedToFocus = false;
    state.focusAnchorX = state.stageAnchorX;
    state.focusAnchorY = state.stageAnchorY;
    state.targetScale = state.minScale;
    state.targetCameraX = initialNode.homeX;
    state.targetCameraY = initialNode.homeY;
    initialNode.glow = 1.2;
    clampCamera();
    updateFocusPanel();
    updateCursor();
    scheduleFrame();
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
    scheduleFrame();
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
        scheduleFrame();
        return;
      }
    }

    const nextHovered = findNodeAt(event.clientX, event.clientY);
    const nextId = nextHovered ? nextHovered.id : '';
    if (state.hoveredNodeId !== nextId) {
      state.hoveredNodeId = nextId;
      updateFocusPanel();
      scheduleFrame();
    }
    updateCursor();
  }

  function handlePointerLeave() {
    state.hoveredNodeId = '';
    updateFocusPanel();
    updateCursor();
    scheduleFrame();
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
    const traversal = focused ? getFocusTraversal(focused) : null;
    const relatedIds = focused ? state.adjacency.get(focused.id) : null;

    if (focused) {
      if (node.id === focused.id) {
        return { emphasis: 1, active: true, related: false, chained: false, hovered: false };
      }
      if (relatedIds?.has(node.id)) {
        return { emphasis: 0.7, active: false, related: true, chained: false, hovered: false };
      }
      if (traversal?.depths.has(node.id)) {
        const depth = traversal.depths.get(node.id);
        if (depth > state.maxVisibleDepth) {
          return { emphasis: 0.015, active: false, related: false, chained: false, hovered: false };
        }
        const emphasis = Math.max(0.16, 0.58 - depth * 0.12);
        return { emphasis, active: false, related: false, chained: true, hovered: false };
      }
      if (hovered && node.id === hovered.id) {
        return { emphasis: 0.28, active: false, related: false, chained: false, hovered: true };
      }
      return { emphasis: 0.03, active: false, related: false, chained: false, hovered: false };
    }

    if (hovered && node.id === hovered.id) {
      return { emphasis: 0.8, active: false, related: false, chained: false, hovered: true };
    }

    return { emphasis: 0.38, active: false, related: false, chained: false, hovered: false };
  }

  function updateFrameState() {
    clampCamera();
    state.scale += (state.targetScale - state.scale) * 0.18;
    state.cameraX += (state.targetCameraX - state.cameraX) * 0.1;
    state.cameraY += (state.targetCameraY - state.cameraY) * 0.1;

    nodes.forEach(node => {
      const target = getDisplayTarget(node);
      node.x += (target.x - node.x) * 0.12;
      node.y += (target.y - node.y) * 0.12;
      node.glow *= 0.88;
    });
  }

  function isAnimating() {
    const now = typeof performance !== 'undefined' && performance.now
      ? performance.now()
      : Date.now();
    if (now < state.ambientMotionUntil) return true;
    if (state.dragging || state.pointerDown) return true;
    if (Math.abs(state.scale - state.targetScale) > 0.001) return true;
    if (Math.abs(state.cameraX - state.targetCameraX) > 0.2) return true;
    if (Math.abs(state.cameraY - state.targetCameraY) > 0.2) return true;
    if (nodes.some(node => {
      const target = getDisplayTarget(node);
      return Math.abs(node.x - target.x) > 0.3 || Math.abs(node.y - target.y) > 0.3;
    })) return true;
    return nodes.some(node => node.glow > 0.03);
  }

  function drawBackground() {
    ctx.clearRect(0, 0, state.width, state.height);
    const now = typeof performance !== 'undefined' && performance.now
      ? performance.now()
      : Date.now();
    const introProgress = Math.max(0, Math.min(1, (state.ambientMotionUntil - now) / 1100));
    const introEase = introProgress > 0 ? introProgress * introProgress * (3 - 2 * introProgress) : 0;
    const time = now * 0.001;

    const gradient = ctx.createRadialGradient(
      state.width * 0.52,
      state.height * 0.42,
      0,
      state.width * 0.52,
      state.height * 0.42,
      state.width * 0.78
    );
    gradient.addColorStop(0, 'rgba(15, 18, 24, 0.82)');
    gradient.addColorStop(0.35, 'rgba(11, 14, 20, 0.48)');
    gradient.addColorStop(1, 'rgba(4, 5, 8, 0)');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, state.width, state.height);

    state.stars.forEach(star => {
      const driftWave = Math.sin(time * 1.1 + star.phase);
      const offsetX = star.driftX * introEase * driftWave;
      const offsetY = star.driftY * introEase * Math.cos(time * 0.95 + star.phase);
      const pulse = 0.9 + Math.sin(time * star.pulse + star.phase) * 0.12;
      ctx.beginPath();
      ctx.fillStyle = `rgba(255, 247, 235, ${Math.min(0.72, star.alpha * pulse)})`;
      ctx.shadowBlur = star.glow ? 11 + introEase * 5 : 2;
      ctx.shadowColor = star.glow
        ? 'rgba(255, 243, 224, 0.42)'
        : 'rgba(210, 225, 255, 0.12)';
      ctx.arc(star.x + offsetX, star.y + offsetY, star.radius * (0.96 + pulse * 0.08), 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.shadowBlur = 0;
  }

  function drawLinks() {
    const focused = getFocusedNode();
    if (!focused) return;
    const traversal = getFocusTraversal(focused);
    const layoutMap = getFocusLayoutMap(focused);

    traversal.parents.forEach((parentId, nodeId) => {
      if (!parentId) return;
      const node = state.nodesById.get(nodeId);
      const parent = state.nodesById.get(parentId);
      if (!node || !parent) return;
      const depth = traversal.depths.get(nodeId) || 1;
      if (depth > state.maxVisibleDepth) return;
      const start = worldToScreen(parent.x, parent.y);
      const end = worldToScreen(node.x, node.y);
      const mx = (start.x + end.x) * 0.5;
      const my = (start.y + end.y) * 0.5;
      const dx = end.x - start.x;
      const dy = end.y - start.y;
      const length = Math.max(1, Math.hypot(dx, dy));
      const childPosition = layoutMap.get(nodeId);
      const childAngle = childPosition && typeof childPosition.angle === 'number'
        ? childPosition.angle
        : Math.atan2(node.y - focused.y, node.x - focused.x);
      const curve = depth === 1 ? 18 : 34;
      const cx = mx + Math.cos(childAngle) * curve - (dy / length) * (depth === 1 ? 8 : 18);
      const cy = my + Math.sin(childAngle) * curve + (dx / length) * (depth === 1 ? 8 : 18);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.quadraticCurveTo(cx, cy, end.x, end.y);
      ctx.strokeStyle = depth === 1 ? palette.focusLinkDepth1 : palette.focusLinkDepth2;
      ctx.lineWidth = depth === 1 ? 1.55 : 1.08;
      ctx.globalAlpha = depth === 1 ? 0.9 : 0.62;
      ctx.shadowBlur = depth === 1 ? 10 : 5;
      ctx.shadowColor = depth === 1 ? palette.focusLinkDepth1Glow : palette.focusLinkDepth2Glow;
      ctx.stroke();
      ctx.shadowBlur = 0;
    });

    ctx.globalAlpha = 1;
  }

  function drawNode(node, nodeState) {
    if (!nodeState.active && nodeState.emphasis < 0.018) {
      return;
    }

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

    if (!nodeState.active && nodeState.emphasis < 0.07) {
      return;
    }

    const placeLeft = isLabelOnLeft(node);
    const labelX = placeLeft ? point.x - 11 : point.x + 11;
    const labelY = point.y - 4;
    ctx.textAlign = placeLeft ? 'right' : 'left';
    ctx.font = nodeState.active
      ? '500 15px "Noto Sans JP", sans-serif'
      : nodeState.related
        ? '400 11px "Noto Sans JP", sans-serif'
        : nodeState.chained
          ? '400 10px "Noto Sans JP", sans-serif'
        : '400 9px "Noto Sans JP", sans-serif';
    ctx.lineJoin = 'round';
    ctx.miterLimit = 2;
    ctx.strokeStyle = palette.textOutline;
    ctx.lineWidth = nodeState.active ? 5.5 : nodeState.related ? 4 : 3.2;
    ctx.globalAlpha = nodeState.active ? 0.96 : nodeState.related ? 0.82 : Math.max(0.26, nodeState.emphasis);
    ctx.strokeText(node.label, labelX, labelY);
    ctx.fillStyle = nodeState.active ? palette.activeText : palette.text;
    ctx.globalAlpha = nodeState.active ? 0.98 : nodeState.related ? 0.82 : Math.max(0.24, nodeState.emphasis);
    ctx.fillText(node.label, labelX, labelY);

    ctx.textAlign = 'left';
  }

  function drawNodes() {
    nodes.forEach(node => {
      drawNode(node, getNodeState(node));
    });
    ctx.globalAlpha = 1;
    ctx.shadowBlur = 0;
  }

  function frame() {
    state.frameHandle = 0;
    updateFrameState();
    drawBackground();
    drawLinks();
    drawNodes();
    if (isAnimating()) {
      scheduleFrame();
    }
  }

  function scheduleFrame() {
    if (state.frameHandle) return;
    state.frameHandle = requestAnimationFrame(frame);
  }

  function centerInitialNode() {
    const preferred = state.nodesById.get('photographer:stieglitz');
    const fallback = nodes.find(node => node.type === 'photographer') || nodes[0];
    const initialNode = preferred || fallback;
    if (!initialNode) return;
    state.initialNodeId = initialNode.id;
    state.scale = state.minScale;
    state.targetScale = state.minScale;
    state.cameraX = initialNode.x;
    state.targetCameraX = initialNode.x;
    state.cameraY = initialNode.y;
    state.targetCameraY = initialNode.y;
    state.stageAnchorX = initialNode.x;
    state.stageAnchorY = initialNode.y;
    state.focusAnchorX = state.stageAnchorX;
    state.focusAnchorY = state.stageAnchorY;
    state.focusedNodeId = '';
    state.focusClusterCache = null;
    state.focusTraversalCache = null;
    state.focusLayoutCache = null;
    initialNode.glow = 1.1;
    updateFocusPanel();
  }

  canvas.addEventListener('pointerdown', handlePointerDown);
  canvas.addEventListener('pointermove', handlePointerMove);
  canvas.addEventListener('pointerup', handlePointerUp);
  canvas.addEventListener('pointerleave', handlePointerLeave);
  canvas.addEventListener('wheel', handleWheel, { passive: false });
  window.addEventListener('resize', resize);
  zoomInButton.addEventListener('click', () => nudgeZoom(1.35));
  zoomOutButton.addEventListener('click', () => nudgeZoom(1 / 1.35));
  resetViewButton.addEventListener('click', resetView);

  resize();
  layoutNodes();
  centerInitialNode();
  updateCursor();
  scheduleFrame();
})();
