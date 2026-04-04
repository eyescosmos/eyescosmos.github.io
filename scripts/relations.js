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
  const languageApi = window.PhotoCoordinatesI18n;
  let currentLanguage = languageApi ? languageApi.getLanguage() : 'ja';

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
    ja: {
      photographer: '写真家',
      movement: '運動',
      idea: '思想'
    },
    en: {
      photographer: 'Photographer',
      movement: 'Movement',
      idea: 'Idea'
    }
  };

  const uiText = {
    ja: {
      title: '写真の座標',
      status: '随時更新中',
      subcopy: '世界・日本、各国の写真家、運動、思想の関係をたどるサイトです。',
      note: '※ 本サイトの情報はAIがウェブ上の公開資料をもとに収集・整理したものです。出典を明記していますが、誤りや更新差が含まれる可能性があります。',
      lede: '写真家、運動、思想を大きな平面の上にひらいた試作ページです。<br>クリックで中心に寄せ、もう一度クリックで詳細へ移動します。ドラッグすると広い地図を静かに探索できます。',
      eraLink: '年代から見る',
      movementLink: '表現から見る',
      defaultLabel: '写真の座標',
      defaultMeta: '点ではなく名前そのものをたどりながら、関係の地図を横断します。',
      defaultHintPointer: 'クリックで関係を開き、◎で初期表示に戻れます。',
      defaultHintTouch: 'タップで関係を開き、◎で初期表示に戻れます。',
      focusedHint: '固定中。線はこの対象から辿れるつながりを示します。もう一度クリックで新しいタブに詳細を開きます。',
      dragHint: '固定中。ドラッグで地図を移動できます。',
      notFocusedHint: 'まだ固定されていません。クリックするとこの名前が中心になります。',
      direct: '直接',
      visible: '表示中'
    },
    en: {
      title: 'Photo Coordinates',
      status: 'Updating',
      subcopy: 'A site that traces photographic history through relationships among photographers, movements, and ideas.',
      note: 'This site gathers and organizes information from publicly available web sources with AI assistance. Sources are listed, but errors or outdated details may remain.',
      lede: 'This prototype lays photographers, movements, and ideas across one large plane.<br>Click once to bring a node to the center, click again to open the detail page, and drag to explore the map quietly.',
      eraLink: 'Browse by Era',
      movementLink: 'Browse by Movement',
      defaultLabel: 'Photo Coordinates',
      defaultMeta: 'Follow names rather than dots, and move across a map of relationships.',
      defaultHintPointer: 'Click to reveal relationships, and use ◎ to return to the default view.',
      defaultHintTouch: 'Tap to reveal relationships, and use ◎ to return to the default view.',
      focusedHint: 'Pinned. The lines show what can be traced outward from this subject. Click once more to open the detail page in a new tab.',
      dragHint: 'Pinned. You can drag to move around the map.',
      notFocusedHint: 'This node is not pinned yet. Click to bring it to the center.',
      direct: 'Direct',
      visible: 'Visible'
    }
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

  function localizedUi(key) {
    return uiText[currentLanguage][key] || uiText.ja[key] || '';
  }

  function getNodeLabel(node) {
    if (!node) return '';
    if (currentLanguage === 'en') return node.labelEn || node.label || '';
    return node.labelJa || node.label || '';
  }

  function refreshNodeMetrics() {
    nodes.forEach(node => {
      node.hitWidth = Math.max(90, getNodeLabel(node).length * 16 + 36);
    });
  }

  function applyLanguageControls() {
    document.querySelectorAll('.lang-btn').forEach(button => {
      button.classList.toggle('active', button.dataset.lang === currentLanguage);
    });
  }

  function initializeLanguageControls() {
    applyLanguageControls();
    document.querySelectorAll('.lang-btn').forEach(button => {
      button.addEventListener('click', () => {
        if (button.dataset.lang === currentLanguage) return;
        currentLanguage = languageApi ? languageApi.setLanguage(button.dataset.lang) : button.dataset.lang;
        applyLanguageControls();
        applyStaticTranslations();
        refreshNodeMetrics();
        updateFocusPanel();
        updateCursor();
        scheduleFrame();
      });
    });
  }

  function applyStaticTranslations() {
    const pageTitleJa = document.documentElement.dataset.pageTitleJa || uiText.ja.title;
    const pageTitleEn = document.documentElement.dataset.pageTitleEn || uiText.en.title;
    const titleEl = document.getElementById('main-title');
    const statusEl = document.getElementById('title-status');
    const subcopyEl = document.getElementById('title-subcopy');
    const noteEl = document.getElementById('title-note');
    const ledeEl = document.getElementById('title-lede');
    const eraLinkEl = document.getElementById('page-link-era');
    const movementLinkEl = document.getElementById('page-link-movement');

    if (titleEl) titleEl.textContent = localizedUi('title');
    if (statusEl) statusEl.textContent = localizedUi('status');
    if (subcopyEl) subcopyEl.textContent = localizedUi('subcopy');
    if (noteEl) noteEl.textContent = localizedUi('note');
    if (ledeEl) ledeEl.innerHTML = localizedUi('lede');
    if (eraLinkEl) eraLinkEl.textContent = localizedUi('eraLink');
    if (movementLinkEl) movementLinkEl.textContent = localizedUi('movementLink');
    document.title = currentLanguage === 'en' ? pageTitleEn : pageTitleJa;
  }

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

  function relaxVertically(list, minGap, iterations) {
    const ordered = [...list].sort((a, b) => a.y - b.y);
    for (let step = 0; step < iterations; step += 1) {
      for (let index = 1; index < ordered.length; index += 1) {
        const upper = ordered[index - 1];
        const lower = ordered[index];
        const gap = lower.y - upper.y;
        if (gap >= minGap) continue;
        const push = (minGap - gap) * 0.5;
        upper.y -= push;
        lower.y += push;
      }
    }
  }

  function repelCrowdedNodes(list, minXGap, minYGap, iterations) {
    for (let step = 0; step < iterations; step += 1) {
      for (let index = 0; index < list.length; index += 1) {
        for (let otherIndex = index + 1; otherIndex < list.length; otherIndex += 1) {
          const node = list[index];
          const other = list[otherIndex];
          const dx = other.x - node.x;
          const dy = other.y - node.y;
          const overlapX = minXGap - Math.abs(dx);
          const overlapY = minYGap - Math.abs(dy);
          if (overlapX <= 0 || overlapY <= 0) continue;

          if (overlapX < overlapY) {
            const push = overlapX * 0.52;
            const direction = dx === 0 ? (stableSortValue(`${node.id}:${other.id}`) % 2 ? 1 : -1) : Math.sign(dx);
            node.x -= direction * push;
            other.x += direction * push;
          } else {
            const push = overlapY * 0.52;
            const direction = dy === 0 ? (stableSortValue(`${node.id}:${other.id}:y`) % 2 ? 1 : -1) : Math.sign(dy);
            node.y -= direction * push;
            other.y += direction * push;
          }
        }
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
    state.ambientMotionUntil = now + 1600;
    state.stars = Array.from(
      { length: Math.max(320, Math.round((state.width * state.height) / 7000)) },
      () => {
        const bright = Math.random() > 0.78;
        return {
          x: Math.random() * state.width,
          y: Math.random() * state.height,
          radius: 0.55 + Math.random() * 0.7 + (bright ? 0.45 + Math.random() * 0.35 : 0),
          alpha: 0.14 + Math.random() * 0.34 + (bright ? 0.08 : 0),
          phase: Math.random() * Math.PI * 2,
          driftX: (Math.random() - 0.5) * 8.2,
          driftY: (Math.random() - 0.5) * 7.1,
          pulse: 0.9 + Math.random() * 0.22,
          glow: bright ? 1 : Math.random() > 0.6 ? 1 : 0
        };
      }
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

    const eraSpacing = 1180;
    const startX = -((eraOrder.length - 1) * eraSpacing) / 2;
    const photographerByEra = new Map();
    const rowsPerEra = 8;
    const rowSpacing = 420;
    const columnSpacing = 420;

    photographers.forEach(node => {
      const list = photographerByEra.get(node.era) || [];
      list.push(node);
      photographerByEra.set(node.era, list);
    });

    eraOrder.forEach((eraId, eraIndex) => {
      const eraNodes = photographerByEra.get(eraId) || [];
      const localRows = Math.min(10, Math.max(rowsPerEra, Math.ceil(Math.sqrt(Math.max(eraNodes.length, 1))) + 2));
      const densityBoost = Math.max(0, eraNodes.length - 10);
      const rightSideBoost = eraIndex / Math.max(1, eraOrder.length - 1);
      const localRowSpacing = rowSpacing + Math.min(180, densityBoost * 12) + rightSideBoost * 180;
      const localColumnSpacing = columnSpacing + Math.min(220, densityBoost * 14);
      const verticalWaveBoost = 190 + rightSideBoost * 150;
      const verticalJitter = 360 + rightSideBoost * 180;
      const lowerBiasStrength = 260 + rightSideBoost * 140;
      const columns = Math.max(1, Math.ceil(eraNodes.length / localRows));
      eraNodes.forEach((node, index) => {
        const column = Math.floor(index / localRows);
        const row = index % localRows;
        const rowOffset = (row - (localRows - 1) / 2) * localRowSpacing;
        const columnOffset = (column - (columns - 1) / 2) * localColumnSpacing;
        const eraWave = Math.sin(eraIndex * 0.92 + column * 0.55) * verticalWaveBoost;
        const columnDrift = Math.cos((row + 1) * 0.7 + eraIndex * 0.45) * 80;
        const lowerBias = ((row / Math.max(1, localRows - 1)) - 0.35) * lowerBiasStrength;
        node.x =
          startX +
          eraIndex * eraSpacing +
          columnOffset +
          columnDrift +
          jitter(node.id, 260);
        node.y =
          rowOffset +
          eraWave +
          lowerBias +
          jitter(`${node.id}:y`, verticalJitter);
      });

      relaxHorizontally(eraNodes, 260, 14);
      relaxVertically(eraNodes, 220 + rightSideBoost * 60, 12);
      repelCrowdedNodes(eraNodes, 220, 130 + rightSideBoost * 60, 12);
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
      const row = index % 7;
      node.x = movementUsage.get(node.id) + jitter(node.id, 420);
      node.y = -1980 + row * 260 + jitter(`${node.id}:y`, 180);
    });

    relaxHorizontally(sortedMovements, 260, 18);
    relaxVertically(sortedMovements, 120, 10);
    repelCrowdedNodes(sortedMovements, 220, 90, 8);

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
      const row = index % 6;
      node.x = ideaUsage.get(node.id) + jitter(node.id, 460);
      node.y = 2380 + row * 320 + jitter(`${node.id}:y`, 240);
    });

    relaxHorizontally(sortedIdeas, 280, 18);
    relaxVertically(sortedIdeas, 120, 10);
    repelCrowdedNodes(sortedIdeas, 240, 100, 8);

    const allX = nodes.map(node => node.x);
    const allY = nodes.map(node => node.y);
    state.world.minX = Math.min(...allX) - 1400;
    state.world.maxX = Math.max(...allX) + 1400;
    state.world.minY = Math.min(...allY) - 1400;
    state.world.maxY = Math.max(...allY) + 1900;

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
    const baseScale = Math.max(1.02, Math.min(1.95, fitX * 8.0, fitY * 8.0));
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
      return currentNode.id === focused.id && edge.type === 'idea';
    }

    if (focused.type === 'photographer') {
      if (currentNode.id === focused.id) {
        return edge.type === 'movement_peer' || edge.type === 'era' || edge.type === 'belongs_to';
      }
      if (currentNode.type === 'movement') {
        return edge.type === 'belongs_to' || edge.type === 'influences' || edge.type === 'idea';
      }
      if (currentNode.type === 'photographer') {
        return edge.type === 'movement_peer' || edge.type === 'era' || edge.type === 'belongs_to';
      }
      return false;
    }

    if (focused.type === 'movement') {
      if (currentNode.id === focused.id) {
        return edge.type === 'belongs_to' || edge.type === 'influences' || edge.type === 'idea';
      }
      if (currentNode.type === 'movement') {
        return edge.type === 'belongs_to' || edge.type === 'influences' || edge.type === 'idea';
      }
      if (currentNode.type === 'photographer') {
        return edge.type === 'movement_peer' || edge.type === 'era' || edge.type === 'belongs_to';
      }
      return false;
    }

    if (focused.type === 'idea') {
      if (currentNode.id === focused.id) {
        return edge.type === 'idea';
      }
      if (currentNode.type === 'movement') {
        return edge.type === 'belongs_to' || edge.type === 'influences';
      }
      if (currentNode.type === 'photographer') {
        return edge.type === 'movement_peer' || edge.type === 'era';
      }
      return false;
    }

    return false;
  }

  function prioritizeTraversalEdges(focused, currentNode, currentDepth, edges) {
    const ranked = [...edges].sort((a, b) => {
      const scoreDiff = scoreTraversalEdge(focused, currentNode, b) - scoreTraversalEdge(focused, currentNode, a);
      if (scoreDiff !== 0) return scoreDiff;
      return stableSortValue(`${currentNode.id}:${a.id}`) - stableSortValue(`${currentNode.id}:${b.id}`);
    });

    const rootPhotographerCount = focused.type === 'movement'
      ? (state.neighborEdges.get(focused.id) || []).filter(edge => {
        const node = state.nodesById.get(edge.id);
        return edge.type === 'belongs_to' && node?.type === 'photographer';
      }).length
      : 0;

    const limit = currentDepth === 0
      ? focused.type === 'photographer'
        ? 7
        : focused.type === 'movement'
          ? Math.min(12, Math.max(8, rootPhotographerCount + 2))
          : 6
      : currentNode.type === 'movement'
        ? 6
        : 5;

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
      if (currentNode.id === focused.id) {
        if (nextNode.type === 'photographer') score += 150;
        if (edge.type === 'belongs_to') score += 95;
        if (nextNode.type === 'movement') score += 48;
        if (edge.type === 'influences') score += 34;
        if (nextNode.type === 'idea') score += 16;
        if (edge.type === 'idea') score += 12;
      } else if (currentNode.type === 'movement') {
        if (nextNode.type === 'photographer') score += 116;
        if (edge.type === 'belongs_to') score += 72;
        if (nextNode.type === 'movement') score += 38;
        if (edge.type === 'influences') score += 24;
        if (nextNode.type === 'idea') score += 10;
      } else if (currentNode.type === 'photographer') {
        if (nextNode.type === 'photographer') score += 96;
        if (edge.type === 'movement_peer') score += 56;
        if (edge.type === 'era') score += 28;
        if (edge.type === 'belongs_to') score += 8;
      }
    } else {
      if (currentNode.id === focused.id) {
        if (nextNode.type === 'movement') score += 130;
        if (edge.type === 'idea') score += 90;
      } else if (currentNode.type === 'movement') {
        if (nextNode.type === 'photographer') score += 92;
        if (edge.type === 'belongs_to') score += 56;
        if (nextNode.type === 'movement') score += 24;
        if (edge.type === 'influences') score += 18;
      } else if (currentNode.type === 'photographer') {
        if (nextNode.type === 'photographer') score += 70;
        if (edge.type === 'movement_peer') score += 34;
        if (edge.type === 'era') score += 18;
      }
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
      labelEl.textContent = localizedUi('defaultLabel');
      metaEl.textContent = localizedUi('defaultMeta');
      hintEl.textContent = prefersCoarse
        ? localizedUi('defaultHintTouch')
        : localizedUi('defaultHintPointer');
      return;
    }

    const relatedCount = state.adjacency.get(target.id)?.size || 0;
    const traversal = node && node.id === target.id ? getFocusTraversal(target) : null;
    const reachCount = traversal
      ? Array.from(traversal.depths.values()).filter(depth => depth > 0 && depth <= state.maxVisibleDepth).length
      : 0;
    labelEl.textContent = getNodeLabel(target);
    metaEl.textContent = `${typeLabel[currentLanguage][target.type]} / ${localizedUi('direct')} ${relatedCount} / ${localizedUi('visible')} ${reachCount}`;
    if (node && node.id === target.id) {
      hintEl.textContent = target.url
        ? localizedUi('focusedHint')
        : localizedUi('dragHint');
    } else {
      hintEl.textContent = localizedUi('notFocusedHint');
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
    const targetUrl = currentLanguage === 'en'
      ? (node.urlEn || node.urlJa || node.url)
      : (node.urlJa || node.urlEn || node.url);
    if (!targetUrl) return;
    node.glow = 2;
    scheduleFrame();
    const popup = window.open(targetUrl, '_blank');
    if (!popup) {
      window.location.href = targetUrl;
      return;
    }
    popup.opener = null;
  }

  function getRequestedFocusNodeId() {
    const params = new URLSearchParams(window.location.search);
    const focusId = params.get('focus');
    if (focusId && state.nodesById.has(focusId)) {
      return focusId;
    }
    return '';
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

    const targetUrl = currentLanguage === 'en'
      ? (node.urlEn || node.urlJa || node.url)
      : (node.urlJa || node.urlEn || node.url);

    if (state.focusedNodeId === node.id && targetUrl) {
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
    const introProgress = Math.max(0, Math.min(1, (state.ambientMotionUntil - now) / 1600));
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

    const nebulaA = ctx.createRadialGradient(
      state.width * 0.68,
      state.height * 0.28,
      0,
      state.width * 0.68,
      state.height * 0.28,
      state.width * 0.34
    );
    nebulaA.addColorStop(0, 'rgba(104, 138, 255, 0.08)');
    nebulaA.addColorStop(1, 'rgba(104, 138, 255, 0)');
    ctx.fillStyle = nebulaA;
    ctx.fillRect(0, 0, state.width, state.height);

    const nebulaB = ctx.createRadialGradient(
      state.width * 0.24,
      state.height * 0.7,
      0,
      state.width * 0.24,
      state.height * 0.7,
      state.width * 0.28
    );
    nebulaB.addColorStop(0, 'rgba(226, 192, 146, 0.06)');
    nebulaB.addColorStop(1, 'rgba(226, 192, 146, 0)');
    ctx.fillStyle = nebulaB;
    ctx.fillRect(0, 0, state.width, state.height);

    state.stars.forEach(star => {
      const driftWave = Math.sin(time * 1.25 + star.phase);
      const offsetX = star.driftX * introEase * driftWave;
      const offsetY = star.driftY * introEase * Math.cos(time * 1.08 + star.phase);
      const pulse = 0.9 + Math.sin(time * star.pulse + star.phase) * 0.12;
      ctx.beginPath();
      ctx.fillStyle = `rgba(255, 247, 235, ${Math.min(0.85, star.alpha * pulse)})`;
      ctx.shadowBlur = star.glow ? 15 + introEase * 6 : 3;
      ctx.shadowColor = star.glow
        ? 'rgba(255, 243, 224, 0.52)'
        : 'rgba(210, 225, 255, 0.16)';
      ctx.arc(star.x + offsetX, star.y + offsetY, star.radius * (0.96 + pulse * 0.08), 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.shadowBlur = 0;
  }

  function drawLinks() {
    const focused = getFocusedNode();
    if (!focused) return;
    const traversal = getFocusTraversal(focused);

    traversal.parents.forEach((parentId, nodeId) => {
      if (!parentId) return;
      const node = state.nodesById.get(nodeId);
      const parent = state.nodesById.get(parentId);
      if (!node || !parent) return;
      const depth = traversal.depths.get(nodeId) || 1;
      if (depth > state.maxVisibleDepth) return;
      const start = worldToScreen(parent.x, parent.y);
      const end = worldToScreen(node.x, node.y);
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.strokeStyle = depth === 1 ? palette.focusLinkDepth1 : palette.focusLinkDepth2;
      ctx.lineWidth = depth === 1 ? 1.4 : 1.02;
      ctx.globalAlpha = depth === 1 ? 0.92 : 0.56;
      ctx.shadowBlur = depth === 1 ? 9 : 4;
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
    const prominenceBoost = node.type === 'photographer' && node.prominence ? 1.15 : 0;
    const baseRadius = node.type === 'photographer'
      ? 2.15 + prominenceBoost
      : node.type === 'movement'
        ? 1.65
        : 1.45;
    const radius = baseRadius + (nodeState.active ? 3.2 : nodeState.related ? 1.6 : 0) + node.glow;
    const lightBoost = node.type === 'photographer' && node.prominence ? 0.14 : 0;
    const coreBoost = node.type === 'photographer' && node.prominence ? 0.18 : 0;

    ctx.beginPath();
    ctx.fillStyle = palette[node.type];
    ctx.globalAlpha = 0.16 + nodeState.emphasis * (0.82 + lightBoost);
    ctx.shadowBlur = 12 + nodeState.emphasis * 18 + prominenceBoost * 10;
    ctx.shadowColor = palette[node.type];
    ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.fillStyle = '#ffffff';
    ctx.globalAlpha = 0.11 + nodeState.emphasis * (0.38 + coreBoost);
    ctx.arc(point.x, point.y, Math.max(0.7, radius * (0.36 + coreBoost * 0.08)), 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    if (!nodeState.active && nodeState.emphasis < 0.07) {
      return;
    }

    const label = getNodeLabel(node);
    const placeLeft = isLabelOnLeft(node);
    const labelX = placeLeft ? point.x - 11 : point.x + 11;
    const labelY = point.y - 4;
    ctx.textAlign = placeLeft ? 'right' : 'left';
    ctx.font = nodeState.active
      ? '500 15px "Noto Sans JP", sans-serif'
      : nodeState.related
        ? `400 ${node.type === 'photographer' && node.prominence ? 12 : 11}px "Noto Sans JP", sans-serif`
        : nodeState.chained
          ? `400 ${node.type === 'photographer' && node.prominence ? 11 : 10}px "Noto Sans JP", sans-serif`
        : `400 ${node.type === 'photographer' && node.prominence ? 10 : 9}px "Noto Sans JP", sans-serif`;
    ctx.lineJoin = 'round';
    ctx.miterLimit = 2;
    ctx.strokeStyle = palette.textOutline;
    ctx.lineWidth = nodeState.active ? 5.5 : nodeState.related ? 4 : 3.2;
    ctx.globalAlpha = nodeState.active ? 0.96 : nodeState.related ? 0.82 : Math.max(0.26, nodeState.emphasis);
    ctx.strokeText(label, labelX, labelY);
    ctx.fillStyle = nodeState.active ? palette.activeText : palette.text;
    ctx.globalAlpha = nodeState.active ? 0.98 : nodeState.related ? 0.82 : Math.max(0.24, nodeState.emphasis);
    ctx.fillText(label, labelX, labelY);

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

    const requestedFocusId = getRequestedFocusNodeId();
    if (requestedFocusId) {
      setFocusedNode(requestedFocusId);
    }
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

  initializeLanguageControls();
  applyStaticTranslations();
  refreshNodeMetrics();
  resize();
  layoutNodes();
  centerInitialNode();
  updateCursor();
  scheduleFrame();
})();
