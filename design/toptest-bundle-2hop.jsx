/* global React, ReactDOM */
const { useState, useEffect, useRef, useMemo, useCallback } = React;

function ensureTopPageManualPhotographers() {
  if (!Array.isArray(window.PHOTOGRAPHERS)) return;
  const existing = new Set(window.PHOTOGRAPHERS.map((p) => p && p.id));
  const additions = [
    {
      id: 'irving-penn',
      name: 'アーヴィング・ペン',
      nameJa: 'アーヴィング・ペン',
      nameEn: 'Irving Penn',
      country: 'アメリカ',
      nationality: 'US',
      flag: '🇺🇸',
      years: '1917-2009',
      era: '1930',
      movements: ['モダニズム', 'ストレート写真', 'タイポロジー写真'],
      influence: 8.9,
      url: 'https://eyescosmos.github.io/photographers/irving-penn.html',
      urlEn: 'https://eyescosmos.github.io/en/photographers/irving-penn.html',
      x: 0.49,
      y: 0.43
    },
    {
      id: 'richard-avedon',
      name: 'リチャード・アヴェドン',
      nameJa: 'リチャード・アヴェドン',
      nameEn: 'Richard Avedon',
      country: 'アメリカ',
      nationality: 'US',
      flag: '🇺🇸',
      years: '1923-2004',
      era: '1950',
      movements: ['フォトジャーナリズム', 'ドキュメンタリー', 'ステージド写真'],
      influence: 8.9,
      url: 'https://eyescosmos.github.io/photographers/richard-avedon.html',
      urlEn: 'https://eyescosmos.github.io/en/photographers/richard-avedon.html',
      x: 0.52,
      y: 0.47
    },
    {
      id: 'ernest-cole',
      name: 'アーネスト・コール',
      nameJa: 'アーネスト・コール',
      nameEn: 'Ernest Cole',
      country: '南アフリカ',
      nationality: 'ZA',
      flag: '🇿🇦',
      years: '1940-1990',
      era: '1950',
      movements: ['フォトジャーナリズム', '社会ドキュメンタリー', 'ドキュメンタリー'],
      influence: 8.8,
      url: 'https://eyescosmos.github.io/photographers/ernest-cole.html',
      urlEn: 'https://eyescosmos.github.io/en/photographers/ernest-cole.html',
      x: 0.31,
      y: 0.61
    },
    {
      id: 'pieter-hugo',
      name: 'ピーター・ヒューゴ',
      nameJa: 'ピーター・ヒューゴ',
      nameEn: 'Pieter Hugo',
      country: '南アフリカ',
      nationality: 'ZA',
      flag: '🇿🇦',
      years: '1976-',
      era: '2000',
      movements: ['ポートレート', '社会的写真', 'コンセプチュアルアート'],
      influence: 7.4,
      url: 'https://eyescosmos.github.io/photographers/pieter-hugo.html',
      urlEn: 'https://eyescosmos.github.io/en/photographers/pieter-hugo.html',
      x: 0.73,
      y: 0.76
    },
    {
      id: 'tokuko-ushioda',
      name: '潮田登久子',
      nameJa: '潮田登久子',
      nameEn: 'Tokuko Ushioda',
      country: '日本',
      nationality: 'JP',
      flag: '🇯🇵',
      years: '1940-',
      era: '1970',
      movements: ['日本写真', '私写真', 'タイポロジー写真', 'プライベート写真'],
      influence: 7.2,
      url: 'https://eyescosmos.github.io/photographers/tokuko-ushioda.html',
      urlEn: 'https://eyescosmos.github.io/en/photographers/tokuko-ushioda.html',
      x: 0.58,
      y: 0.66
    }
  ];
  additions.forEach((photographer) => {
    if (!existing.has(photographer.id)) {
      window.PHOTOGRAPHERS.push(photographer);
      existing.add(photographer.id);
    }
  });

  if (!Array.isArray(window.CONNECTIONS)) return;
  const connectionKey = ([a, b, move]) => `${a}|${b}|${move}`;
  const connectionKeys = new Set(window.CONNECTIONS.map(connectionKey));
  [
    ['irving-penn', 'richard-avedon', 'ステージド写真'],
    ['irving-penn', 'strand', 'ストレート写真'],
    ['irving-penn', 'sander', 'タイポロジー写真'],
    ['richard-avedon', 'irving-penn', 'ステージド写真'],
    ['richard-avedon', 'capa', 'フォトジャーナリズム'],
    ['richard-avedon', 'arbus', 'ドキュメンタリー'],
    ['ernest-cole', 'riis', '社会ドキュメンタリー'],
    ['ernest-cole', 'lewis-hine', '社会ドキュメンタリー'],
    ['ernest-cole', 'capa', 'フォトジャーナリズム'],
    ['pieter-hugo', 'arbus', 'ポートレート'],
    ['pieter-hugo', 'mapplethorpe', 'ポートレート'],
    ['pieter-hugo', 'sherman', 'コンセプチュアルアート'],
    ['tokuko-ushioda', 'rinko-kawauchi', '日本写真'],
    ['tokuko-ushioda', 'araki', '私写真'],
    ['tokuko-ushioda', 'becher', 'タイポロジー写真'],
    ['tokuko-ushioda', 'yurie-nagashima', 'プライベート写真']
  ].forEach((connection) => {
    if (existing.has(connection[0]) && existing.has(connection[1]) && !connectionKeys.has(connectionKey(connection))) {
      window.CONNECTIONS.push(connection);
      connectionKeys.add(connectionKey(connection));
    }
  });
}

ensureTopPageManualPhotographers();

// ======================================================
// Starfield (ambient background dust)
// ======================================================
function Starfield({ density = 260, theme = 'dark' }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const c = canvasRef.current;if (!c) return;
    const ctx = c.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    let stars = [];
    let raf;

    const resize = () => {
      c.width = window.innerWidth * dpr;
      c.height = window.innerHeight * dpr;
      c.style.width = window.innerWidth + 'px';
      c.style.height = window.innerHeight + 'px';
      stars = Array.from({ length: density }, () => ({
        x: Math.random() * c.width,
        y: Math.random() * c.height,
        r: Math.random() * 1.2 * dpr + 0.2 * dpr,
        a: Math.random() * 0.6 + 0.2,
        t: Math.random() * Math.PI * 2,
        speed: Math.random() * 0.006 + 0.002
      }));
    };
    resize();
    window.addEventListener('resize', resize);

    const draw = () => {
      ctx.clearRect(0, 0, c.width, c.height);
      const baseColor = theme === 'light' ? '20, 24, 32' : '255, 250, 240';
      for (const s of stars) {
        s.t += s.speed;
        const alpha = s.a * (0.55 + 0.45 * Math.sin(s.t));
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${baseColor}, ${alpha * (theme === 'light' ? 0.35 : 1)})`;
        ctx.fill();
      }
      raf = requestAnimationFrame(draw);
    };
    draw();
    return () => {cancelAnimationFrame(raf);window.removeEventListener('resize', resize);};
  }, [density, theme]);

  return <canvas ref={canvasRef} className="starfield" />;
}

// ======================================================
// Helper: build adjacency
// ======================================================
function useGraph() {
  return useMemo(() => {
    ensureTopPageManualPhotographers();
    const photographers = window.PHOTOGRAPHERS;
    const byId = Object.fromEntries(photographers.map((p) => [p.id, p]));
    const adj = {};
    const edges = window.CONNECTIONS.map(([a, b, move]) => {
      adj[a] = adj[a] || [];adj[b] = adj[b] || [];
      adj[a].push({ id: b, move });
      adj[b].push({ id: a, move });
      return { a, b, move };
    });
    return { photographers, byId, adj, edges };
  }, []);
}

function isMobileViewportWidth(width) {
  return width < 700;
}

// ======================================================
// Main Constellation View
// ======================================================
function Constellation({ mode, selected, onSelect, hovered, onHover, tweaks, filter, isEnglish = false }) {
  const { photographers, byId, adj, edges } = useGraph();
  const stageRef = useRef(null);
  const [viewport, setViewport] = useState({ w: 1200, h: 800 });
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [zoom, setZoom] = useState(1);
  const draggingRef = useRef(null);
  const dragFrameRef = useRef(null);
  const pendingPanRef = useRef(null);
  const panRef = useRef({ x: 0, y: 0 });
  const zoomRef = useRef(1);
  const viewAnimRef = useRef(null);
  const lastPointerSelectRef = useRef({ id: null, time: 0 });
  const onSelectRef = useRef(onSelect);
  const labelFor = useCallback((p) => isEnglish ? (p.nameEn || p.name || p.nameJa || p.id) : (p.name || p.nameJa || p.nameEn || p.id), [isEnglish]);

  useEffect(() => {
    onSelectRef.current = onSelect;
  }, [onSelect]);

  const flushDragPan = () => {
    dragFrameRef.current = null;
    const nextPan = pendingPanRef.current;
    if (!nextPan) return;
    pendingPanRef.current = null;
    panRef.current = nextPan;
    setPan(nextPan);
  };

  useEffect(() => {
    const measure = () => {
      if (!stageRef.current) return;
      const r = stageRef.current.getBoundingClientRect();
      setViewport({ w: r.width, h: r.height });
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, []);

  // Map data x/y (0-1) to viewport pixels, with padding for labels.
  // Spread tweak expands stars beyond the viewport — drag to explore.
  // Zoom scales positions around the viewport centre so that selecting a
  // star both pans it to centre AND magnifies surrounding constellation.
  const padX = Math.max(120, viewport.w * 0.12);
  const padY = Math.max(100, viewport.h * 0.14);
  const cx = viewport.w / 2;
  const cy = viewport.h / 2;
  const isMobileViewport = isMobileViewportWidth(viewport.w);
  const spread = tweaks.spread || 1;
  const getViewportInsets = () => isMobileViewport
    ? { left: 22, right: 22, top: 186, bottom: 126 }
    : { left: Math.min(360, viewport.w * 0.29), right: 90, top: 122, bottom: 92 };
  const toSpreadPx = (p) => {
    const baseX = padX + p.x * (viewport.w - padX * 2);
    const baseY = padY + p.y * (viewport.h - padY * 2);
    return {
      x: cx + (baseX - cx) * spread,
      y: cy + (baseY - cy) * spread
    };
  };
  const toPx = (p) => {
    const stretched = toSpreadPx(p);
    // Apply per-star animated offset (neighbors glide toward selected)
    const off = offsetsRef.current[p.id] || { dx: 0, dy: 0 };
    return {
      x: cx + (stretched.x + off.dx - cx) * zoom + pan.x,
      y: cy + (stretched.y + off.dy - cy) * zoom + pan.y
    };
  };

  // ---- Animated star offsets ---------------------------------------
  // When a star is selected, its neighbors glide toward it (clamped to a
  // radius), so the constellation forms near the tapped star regardless of
  // their "true" positions. Pan/zoom stay fixed — only stars move.
  const [offsets, setOffsets] = useState({}); // { id: {dx, dy} } in px
  const offsetsRef = useRef({});
  const animRef = useRef(null);
  const buildSelectionTargets = (selectedId) => {
    const targetOffsets = {};
    if (!selectedId) return { memberIds: null, targetOffsets, depthMap: null };
    const focus = byId[selectedId];
    if (!focus) return { memberIds: null, targetOffsets, depthMap: null };

    const hops = tweaks.hops || 1;
    const memberIds = new Set([selectedId]);
    const depthMap = new Map([[selectedId, 0]]);
    let frontier = [selectedId];
    for (let h = 0; h < hops; h++) {
      const next = [];
      frontier.forEach((id) => (adj[id] || []).forEach((n) => {
        if (!memberIds.has(n.id)) {
          memberIds.add(n.id);
          depthMap.set(n.id, h + 1);
          next.push(n.id);
        }
      }));
      frontier = next;
      if (!frontier.length) break;
    }

    const unit = Math.min(viewport.w, viewport.h);
    const focusBase = toSpreadPx(focus);
    const activeEntries = Array.from(memberIds).map((id) => {
      const photographer = byId[id];
      const base = toSpreadPx(photographer);
      const depth = depthMap.get(id) || 0;
      const rawDx = base.x - focusBase.x;
      const rawDy = base.y - focusBase.y;
      const rawDist = Math.hypot(rawDx, rawDy) || 1;
      const ideal = depth === 0
        ? { x: focusBase.x, y: focusBase.y }
        : { x: base.x, y: base.y };
      return { id, depth, base, ideal, rawDist };
    });

    const entryById = new Map(activeEntries.map((entry) => [entry.id, entry]));
    const specialFocusSpread = selectedId === 'steichen'
      ? 1.2
      : selectedId === 'capa'
        ? 1.16
        : 1;
    const specialAngleSpread = selectedId === 'steichen'
      ? 1.16
      : selectedId === 'capa'
        ? 1.12
        : 1;
    const firstDegreeIds = activeEntries.filter((entry) => entry.depth === 1).map((entry) => entry.id);
    const crowdBoost = Math.max(0, Math.min(6, firstDegreeIds.length - 3));
    const denseBoost = Math.max(0, firstDegreeIds.length - 5);
    const positions = new Map(activeEntries.map((entry) => [entry.id, { ...entry.ideal }]));
    const idealMap = new Map(activeEntries.map((entry) => [entry.id, entry.ideal]));
    const depthOf = (id) => depthMap.get(id) || 0;
    const activeEdges = edges.filter((edge) => {
      if (!memberIds.has(edge.a) || !memberIds.has(edge.b)) return false;
      const aDepth = depthOf(edge.a);
      const bDepth = depthOf(edge.b);
      const low = Math.min(aDepth, bDepth);
      const high = Math.max(aDepth, bDepth);
      return (low === 0 && high === 1) || (low === 1 && high === 2);
    });
    const desiredSpacing = (aEntry, bEntry) => {
      const labelFactor = Math.max((byId[aEntry.id]?.name?.length || 4), (byId[bEntry.id]?.name?.length || 4));
      const baseGap = aEntry.depth === 1 && bEntry.depth === 1
        ? 132 + crowdBoost * 20 + denseBoost * 12
        : aEntry.depth === 2 && bEntry.depth === 2
          ? 122 + crowdBoost * 16 + denseBoost * 10
          : 126 + crowdBoost * 18 + denseBoost * 10;
      return (baseGap + Math.min(36, labelFactor * 1.45)) * specialFocusSpread * (isMobileViewport ? 0.62 : 1);
    };
    const averageAngle = (angles) => {
      if (!angles.length) return 0;
      let sx = 0;
      let sy = 0;
      angles.forEach((angle) => {
        sx += Math.cos(angle);
        sy += Math.sin(angle);
      });
      return Math.atan2(sy, sx);
    };
    const normalizeAround = (angle, reference) => {
      let next = angle;
      while (next - reference > Math.PI) next -= Math.PI * 2;
      while (next - reference < -Math.PI) next += Math.PI * 2;
      return next;
    };
    const shortestAngleDelta = (from, to) => normalizeAround(to, from) - from;

    const childIdsByFirst = new Map();
    const parentIdsBySecond = new Map();
    activeEdges.forEach((edge) => {
      const aDepth = depthOf(edge.a);
      const bDepth = depthOf(edge.b);
      let firstId = null;
      let secondId = null;
      if (aDepth === 1 && bDepth === 2) {
        firstId = edge.a;
        secondId = edge.b;
      } else if (aDepth === 2 && bDepth === 1) {
        firstId = edge.b;
        secondId = edge.a;
      }
      if (!firstId || !secondId) return;
      if (!childIdsByFirst.has(firstId)) childIdsByFirst.set(firstId, []);
      childIdsByFirst.get(firstId).push(secondId);
      if (!parentIdsBySecond.has(secondId)) parentIdsBySecond.set(secondId, []);
      parentIdsBySecond.get(secondId).push(firstId);
    });

    const mobileConstellationScale = isMobileViewport ? 0.34 : 1;
    const ringRadius1 = Math.max(
      194 + crowdBoost * 22 + denseBoost * 14,
      unit * (0.255 + crowdBoost * 0.016 + denseBoost * 0.011)
    ) * specialFocusSpread * mobileConstellationScale;
    const ringRadius2 = Math.max(
      ringRadius1 + 148 + crowdBoost * 20 + denseBoost * 14,
      unit * (0.415 + crowdBoost * 0.019 + denseBoost * 0.013)
    ) * specialFocusSpread * mobileConstellationScale;

    const firstDegreeAngleById = new Map();
    const secondDegreeIds = activeEntries.filter((entry) => entry.depth === 2).map((entry) => entry.id);
    const selectedAngleBiasMap = selectedId === 'capa'
      ? new Map([
        ['cartierbresson', -0.16],
        ['robertfrank', 0.1],
        ['william-vandivert', 0.28]
      ])
      : selectedId === 'steichen'
        ? new Map([
          ['jp-野島康三', 0.02],
          ['jp-福原信三', 0.18],
          ['sander', -0.18]
        ])
        : new Map();
    const withSelectedBias = (id, angle) => angle + (selectedAngleBiasMap.get(id) || 0);

    const placeEntriesOnArc = (ids, getAnchorAngle, radius, minGap, spanBias = 1.3) => {
      if (!ids.length) return;
      if (ids.length === 1) {
        const angle = withSelectedBias(ids[0], getAnchorAngle(ids[0]));
        positions.set(ids[0], {
          x: focusBase.x + Math.cos(angle) * radius,
          y: focusBase.y + Math.sin(angle) * radius
        });
        return;
      }

      const center = averageAngle(ids.map((id) => withSelectedBias(id, getAnchorAngle(id))));
      const ordered = ids
        .map((id) => ({
          id,
          anchor: withSelectedBias(id, getAnchorAngle(id)),
          normalized: normalizeAround(withSelectedBias(id, getAnchorAngle(id)), center)
        }))
        .sort((a, b) => a.normalized - b.normalized);

      const rawSpan = Math.max(0.001, ordered[ordered.length - 1].normalized - ordered[0].normalized);
      const targetSpan = Math.min(
        Math.PI * (isMobileViewport ? 1.72 : 1.9),
        Math.max(minGap * (ordered.length - 1), rawSpan * spanBias, 0.62 * (ordered.length - 1))
      );
      const start = center - targetSpan * 0.5;
      ordered.forEach((node, index) => {
        const t = ordered.length === 1 ? 0.5 : index / (ordered.length - 1);
        const angle = start + targetSpan * t;
        positions.set(node.id, {
          x: focusBase.x + Math.cos(angle) * radius,
          y: focusBase.y + Math.sin(angle) * radius
        });
        if (depthOf(node.id) === 1) firstDegreeAngleById.set(node.id, angle);
      });
    };

    placeEntriesOnArc(
      firstDegreeIds,
      (id) => {
        const entry = entryById.get(id);
        const childIds = childIdsByFirst.get(id) || [];
        if (!childIds.length) return Math.atan2(entry.base.y - focusBase.y, entry.base.x - focusBase.x);
        return averageAngle([
          Math.atan2(entry.base.y - focusBase.y, entry.base.x - focusBase.x),
          ...childIds.map((childId) => {
            const child = entryById.get(childId);
            return withSelectedBias(childId, Math.atan2(child.base.y - focusBase.y, child.base.x - focusBase.x));
          })
        ]);
      },
      ringRadius1,
      (0.38 + crowdBoost * 0.055 + denseBoost * 0.035) * specialAngleSpread,
      1.45 + denseBoost * 0.05 + (specialAngleSpread - 1) * 0.8
    );

    placeEntriesOnArc(
      secondDegreeIds,
      (id) => {
        const entry = entryById.get(id);
        const rawAngle = withSelectedBias(id, Math.atan2(entry.base.y - focusBase.y, entry.base.x - focusBase.x));
        const parentAngles = (parentIdsBySecond.get(id) || [])
          .map((parentId) => firstDegreeAngleById.get(parentId))
          .filter((angle) => typeof angle === 'number');
        if (!parentAngles.length) return rawAngle;
        return averageAngle([rawAngle, ...parentAngles, ...parentAngles]);
      },
      ringRadius2,
      (0.29 + crowdBoost * 0.045 + denseBoost * 0.032) * specialAngleSpread,
      1.35 + denseBoost * 0.04 + (specialAngleSpread - 1) * 0.7
    );

    for (let iter = 0; iter < 12; iter += 1) {
      const deltas = new Map(activeEntries.map((entry) => [entry.id, { x: 0, y: 0 }]));

      for (let i = 0; i < activeEntries.length; i += 1) {
        for (let j = i + 1; j < activeEntries.length; j += 1) {
          const aEntry = activeEntries[i];
          const bEntry = activeEntries[j];
          if (aEntry.depth === 0 && bEntry.depth === 0) continue;
          const aPos = positions.get(aEntry.id);
          const bPos = positions.get(bEntry.id);
          let dx = bPos.x - aPos.x;
          let dy = bPos.y - aPos.y;
          let dist = Math.hypot(dx, dy);
          if (dist < 1) {
            dx = 1;
            dy = 0;
            dist = 1;
          }
          const minGap = desiredSpacing(aEntry, bEntry);
          if (dist >= minGap) continue;
          const push = (minGap - dist) * 0.2;
          const ux = dx / dist;
          const uy = dy / dist;
          const aDelta = deltas.get(aEntry.id);
          const bDelta = deltas.get(bEntry.id);
          if (aEntry.depth !== 0) {
            aDelta.x -= ux * push;
            aDelta.y -= uy * push;
          }
          if (bEntry.depth !== 0) {
            bDelta.x += ux * push;
            bDelta.y += uy * push;
          }
        }
      }

      activeEntries.forEach((entry) => {
        if (entry.depth === 0) return;
        const current = positions.get(entry.id);
        const delta = deltas.get(entry.id);
        const idealRadius = entry.depth === 1 ? ringRadius1 : ringRadius2;
        const currentAngle = Math.atan2(current.y - focusBase.y, current.x - focusBase.x);
        const anchor = {
          x: focusBase.x + Math.cos(currentAngle) * idealRadius,
          y: focusBase.y + Math.sin(currentAngle) * idealRadius
        };
        current.x += delta.x + (anchor.x - current.x) * 0.18;
        current.y += delta.y + (anchor.y - current.y) * 0.18;
      });
    }

    const bounds = {
      minX: focusBase.x - Math.max(560 + crowdBoost * 30 + denseBoost * 20, unit * 0.72) * specialFocusSpread * mobileConstellationScale,
      maxX: focusBase.x + Math.max(560 + crowdBoost * 30 + denseBoost * 20, unit * 0.72) * specialFocusSpread * mobileConstellationScale,
      minY: focusBase.y - Math.max(462 + crowdBoost * 22 + denseBoost * 16, unit * 0.6) * specialFocusSpread * mobileConstellationScale,
      maxY: focusBase.y + Math.max(462 + crowdBoost * 22 + denseBoost * 16, unit * 0.6) * specialFocusSpread * mobileConstellationScale
    };
    activeEntries.forEach((entry) => {
      if (entry.depth === 0) return;
      const current = positions.get(entry.id);
      current.x = Math.max(bounds.minX, Math.min(bounds.maxX, current.x));
      current.y = Math.max(bounds.minY, Math.min(bounds.maxY, current.y));
    });

    activeEntries.forEach((entry) => {
      if (entry.depth === 0) return;
      const target = positions.get(entry.id);
      targetOffsets[entry.id] = {
        dx: target.x - entry.base.x,
        dy: target.y - entry.base.y
      };
    });

    return { memberIds, targetOffsets, depthMap };
  };

  useEffect(() => {
    const startOffsets = { ...offsetsRef.current };
    const { targetOffsets } = buildSelectionTargets(selected);
    // Any star not in targetOffsets returns to 0,0

    if (animRef.current) cancelAnimationFrame(animRef.current);
    const t0 = performance.now();
    const dur = 700;
    const ease = (t) => 1 - Math.pow(1 - t, 3);
    // Collect all ids that need to animate (either start or target nonzero)
    const allIds = new Set([...Object.keys(startOffsets), ...Object.keys(targetOffsets)]);
    const tick = (now) => {
      const t = Math.min(1, (now - t0) / dur);
      const e = ease(t);
      const next = {};
      allIds.forEach((id) => {
        const s = startOffsets[id] || { dx: 0, dy: 0 };
        const tg = targetOffsets[id] || { dx: 0, dy: 0 };
        const dx = s.dx + (tg.dx - s.dx) * e;
        const dy = s.dy + (tg.dy - s.dy) * e;
        if (Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5) next[id] = { dx, dy };
      });
      offsetsRef.current = next;
      setOffsets(next);
      if (t < 1) animRef.current = requestAnimationFrame(tick);
    };
    animRef.current = requestAnimationFrame(tick);
    return () => {if (animRef.current) cancelAnimationFrame(animRef.current);};
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, tweaks.hops, tweaks.spread, viewport.w, viewport.h]);

  useEffect(() => {
    const { memberIds, targetOffsets, depthMap } = buildSelectionTargets(selected);
    const nextTargetPan = { x: 0, y: 0 };
    let nextTargetZoom = 1;

    if (selected && memberIds?.size) {
      let minX = Infinity;
      let maxX = -Infinity;
      let minY = Infinity;
      let maxY = -Infinity;

      memberIds.forEach((id) => {
        const photographer = byId[id];
        if (!photographer) return;
        const base = toSpreadPx(photographer);
        const off = targetOffsets[id] || { dx: 0, dy: 0 };
        const x = base.x + off.dx;
        const y = base.y + off.dy;
        const depthForBounds = depthMap?.get(id) || 0;
        const mobilePadX = depthForBounds === 0 ? 40 : 62;
        const mobilePadY = depthForBounds === 0 ? 32 : 44;
        const padForBoundsX = isMobileViewport ? mobilePadX : 190;
        const padForBoundsY = isMobileViewport ? mobilePadY : 150;
        minX = Math.min(minX, x - padForBoundsX);
        maxX = Math.max(maxX, x + padForBoundsX);
        minY = Math.min(minY, y - padForBoundsY);
        maxY = Math.max(maxY, y + padForBoundsY);
      });

      if (Number.isFinite(minX) && Number.isFinite(minY)) {
        const insets = getViewportInsets();
        const availableWidth = Math.max(240, viewport.w - insets.left - insets.right);
        const availableHeight = Math.max(220, viewport.h - insets.top - insets.bottom);
        const boundsWidth = Math.max(220, maxX - minX);
        const boundsHeight = Math.max(220, maxY - minY);
        const fitZoom = Math.max(isMobileViewport ? 1.0 : 0.72, Math.min(isMobileViewport ? 1.3 : 3.2, Math.min(
          availableWidth / boundsWidth,
          availableHeight / boundsHeight
        ) * (isMobileViewport ? 1.18 : 1.08)));
        nextTargetZoom = isMobileViewport ? Math.max(1.02, fitZoom) : fitZoom;

        const desiredScreenX = insets.left + availableWidth * 0.5;
        const desiredScreenY = insets.top + availableHeight * 0.5;
        const boundsCenterX = (minX + maxX) * 0.5;
        const boundsCenterY = (minY + maxY) * 0.5;
        nextTargetPan.x = desiredScreenX - (cx + (boundsCenterX - cx) * nextTargetZoom);
        nextTargetPan.y = desiredScreenY - (cy + (boundsCenterY - cy) * nextTargetZoom);

        if (isMobileViewport) {
          const screenMinX = cx + (minX - cx) * nextTargetZoom + nextTargetPan.x;
          const screenMaxX = cx + (maxX - cx) * nextTargetZoom + nextTargetPan.x;
          const screenMinY = cy + (minY - cy) * nextTargetZoom + nextTargetPan.y;
          const screenMaxY = cy + (maxY - cy) * nextTargetZoom + nextTargetPan.y;
          if (screenMinX < insets.left) nextTargetPan.x += insets.left - screenMinX;
          if (screenMaxX > viewport.w - insets.right) nextTargetPan.x -= screenMaxX - (viewport.w - insets.right);
          if (screenMinY < insets.top) nextTargetPan.y += insets.top - screenMinY;
          if (screenMaxY > viewport.h - insets.bottom) nextTargetPan.y -= screenMaxY - (viewport.h - insets.bottom);
        }
      }
    }

    if (viewAnimRef.current) cancelAnimationFrame(viewAnimRef.current);
    const tick = () => {
      const currentPan = panRef.current;
      const currentZoom = zoomRef.current;
      const nextPan = {
        x: currentPan.x + (nextTargetPan.x - currentPan.x) * 0.1,
        y: currentPan.y + (nextTargetPan.y - currentPan.y) * 0.1
      };
      const nextZoomFrame = currentZoom + (nextTargetZoom - currentZoom) * 0.18;
      const done = Math.abs(nextPan.x - nextTargetPan.x) < 0.2
        && Math.abs(nextPan.y - nextTargetPan.y) < 0.2
        && Math.abs(nextZoomFrame - nextTargetZoom) < 0.001;
      const finalPan = done ? nextTargetPan : nextPan;
      const finalZoom = done ? nextTargetZoom : nextZoomFrame;
      panRef.current = finalPan;
      zoomRef.current = finalZoom;
      setPan(finalPan);
      setZoom(finalZoom);
      if (!done) viewAnimRef.current = requestAnimationFrame(tick);
    };
    viewAnimRef.current = requestAnimationFrame(tick);
    return () => {if (viewAnimRef.current) cancelAnimationFrame(viewAnimRef.current);};
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, tweaks.hops, tweaks.spread, viewport.w, viewport.h]);

  // Filter logic (movement filter from dropdown)
  const passesFilter = (p) => {
    if (!filter) return true;
    if (filter.type === 'movement') return p.movements.includes(filter.value);
    if (filter.type === 'country') return p.country.includes(filter.value);
    if (filter.type === 'era') return p.era === filter.value;
    return true;
  };

  const activeDepths = useMemo(() => {
    if (!selected) return null;
    const hops = tweaks.hops || 1;
    const depths = new Map([[selected, 0]]);
    let frontier = [selected];
    for (let h = 0; h < hops; h++) {
      const next = [];
      frontier.forEach((id) => {
        (adj[id] || []).forEach((n) => {
          if (!depths.has(n.id)) {
            depths.set(n.id, h + 1);
            next.push(n.id);
          }
        });
      });
      frontier = next;
      if (!frontier.length) break;
    }
    return depths;
  }, [selected, adj, tweaks.hops]);
  const activeSet = useMemo(() => activeDepths ? new Set(activeDepths.keys()) : null, [activeDepths]);

  const getConnectionLevel = (aId, bId) => {
    if (!activeDepths) return null;
    const aDepth = activeDepths.get(aId);
    const bDepth = activeDepths.get(bId);
    if (aDepth == null || bDepth == null) return null;
    const low = Math.min(aDepth, bDepth);
    const high = Math.max(aDepth, bDepth);
    if (low === 0 && high === 1) return 1;
    if (low === 1 && high === 2) return 2;
    return null;
  };

  const neighborMoveMap = useMemo(() => {
    if (!selected) return {};
    const m = {};
    (adj[selected] || []).forEach((n) => {m[n.id] = n.move;});
    return m;
  }, [selected, adj]);

  // Drag pan
  const onPointerDown = (e) => {
    if (e.pointerType === 'touch' && e.isPrimary === false) return;
    if (viewAnimRef.current) cancelAnimationFrame(viewAnimRef.current);
    e.currentTarget?.setPointerCapture?.(e.pointerId);
    if (e.cancelable) e.preventDefault();
    const starNode = e.target.closest('.star');
    draggingRef.current = {
      x: e.clientX - panRef.current.x,
      y: e.clientY - panRef.current.y,
      startX: e.clientX,
      startY: e.clientY,
      pointerId: e.pointerId,
      starId: starNode?.dataset?.starId || null,
      dragged: false
    };
  };
  const onPointerMove = (e) => {
    if (!draggingRef.current) return;
    if (e.pointerId !== draggingRef.current.pointerId) return;
    if (e.cancelable) e.preventDefault();
    if (Math.hypot(e.clientX - draggingRef.current.startX, e.clientY - draggingRef.current.startY) > 6) {
      draggingRef.current.dragged = true;
    }
    const nextPan = { x: e.clientX - draggingRef.current.x, y: e.clientY - draggingRef.current.y };
    pendingPanRef.current = nextPan;
    if (!dragFrameRef.current) {
      dragFrameRef.current = requestAnimationFrame(flushDragPan);
    }
  };
  const onPointerUp = (e) => {
    const currentDrag = draggingRef.current;
    if (currentDrag && e?.pointerId !== currentDrag.pointerId) return;
    draggingRef.current = null;
    if (!currentDrag) return;
    if (dragFrameRef.current) {
      cancelAnimationFrame(dragFrameRef.current);
      flushDragPan();
    }
    if (!currentDrag.dragged && currentDrag.starId) {
      e?.preventDefault?.();
      e?.stopPropagation?.();
      lastPointerSelectRef.current = { id: currentDrag.starId, time: performance.now() };
      onSelectRef.current(currentDrag.starId);
    }
  };

  useEffect(() => {
    window.addEventListener('pointermove', onPointerMove, { passive: false });
    window.addEventListener('pointerup', onPointerUp);
    window.addEventListener('pointercancel', onPointerUp);
    return () => {
      window.removeEventListener('pointermove', onPointerMove);
      window.removeEventListener('pointerup', onPointerUp);
      window.removeEventListener('pointercancel', onPointerUp);
      if (dragFrameRef.current) cancelAnimationFrame(dragFrameRef.current);
    };
  }, []);

  // Calculate star render size based on influence + zoom + tweak.
  // Stars scale a bit slower than the canvas zoom so they don't blow up.
  const starSize = (p) => {
    const base = 1.5 + p.influence / 10 * tweaks.starSize;
    return base * (0.85 + zoom * 0.4);
  };

  // Label visibility logic — readability first.
  const shouldShowLabel = (p, depth, isActive, isHovered) => {
    if (isActive || isHovered) return true;
    if (tweaks.labelDensity === 'all') return true;
    if (isMobileViewport) {
      if (selected) return depth === 1 && p.influence >= 7;
      return p.influence >= 9.5;
    }
    if (depth === 1) return true;
    if (depth === 2) return true;
    if (tweaks.labelDensity === 'all') return true;
    if (tweaks.labelDensity === 'important') return p.influence >= 9;
    if (tweaks.labelDensity === 'minimal') return false;
    return p.influence >= 9; // default: minimal labels
  };

  // Compute which non-active labels actually render this frame, with simple
  // collision avoidance against already-placed label rects.
  const labelLayout = useMemo(() => {
    const placed = []; // {x,y,w,h}
    const visible = new Map(); // id -> {dx, dy} offset for label
    // Always keep active/hovered/first-degree first, second-degree after.
    const candidates = photographers.slice().sort((a, b) => {
      const aDepth = activeDepths?.get(a.id);
      const bDepth = activeDepths?.get(b.id);
      const aP = a.id === selected || a.id === hovered ? 4 : aDepth === 1 ? 3 : aDepth === 2 ? 2 : 1;
      const bP = b.id === selected || b.id === hovered ? 4 : bDepth === 1 ? 3 : bDepth === 2 ? 2 : 1;
      if (aP !== bP) return bP - aP;
      return b.influence - a.influence;
    });
    const overlap = (a, b) =>
    Math.abs(a.x - b.x) < (a.w + b.w) / 2 + 14 &&
    Math.abs(a.y - b.y) < (a.h + b.h) / 2 + 8;
    // Try several candidate positions around each star to avoid overlap
    // (below, above, right, left). Active/hovered/neighbor still get priority,
    // but they too go through collision avoidance now that stars gather.
    const offsets = [
    { dx: 0, dy: 18 },
    { dx: 0, dy: -24 },
    { dx: 0, dy: 34 },
    { dx: 0, dy: -40 },
    { dx: 26, dy: 10 },
    { dx: -26, dy: 10 },
    { dx: 30, dy: -14 },
    { dx: -30, dy: -14 },
    { dx: 42, dy: 8 },
    { dx: -42, dy: 8 },
    { dx: 40, dy: -24 },
    { dx: -40, dy: -24 },
    { dx: 0, dy: 50 },
    { dx: 0, dy: -56 }
    ];
    for (const p of candidates) {
      const isActive = p.id === selected;
      const depth = activeDepths?.get(p.id);
      const isHovered = p.id === hovered;
      if (!shouldShowLabel(p, depth, isActive, isHovered)) continue;
      const pos = toPx(p);
      const fontSize = isMobileViewport
        ? isActive ? 11.2 : depth === 1 ? 8.9 : depth === 2 ? 8 : p.influence >= 9 ? 9 : 8.4
        : isActive ? 13 : depth === 2 ? (p.influence >= 8 ? 9.5 : 8.5) : p.influence >= 8 ? 11.5 : 10.5;
      const w = (labelFor(p)?.length || 4) * (fontSize * 0.92) + 8;
      const h = depth === 2 ? 12 : 14;
      let placedRect = null;
      for (const off of offsets) {
        const rect = { x: pos.x + off.dx, y: pos.y + off.dy, w, h, off };
        if (!placed.some((r) => overlap(r, rect))) {
          placedRect = rect;
          break;
        }
      }
      if (!placedRect && (isActive || isHovered || depth === 2)) {
        // Selected/hovered must always show — accept overlap as last resort
        placedRect = { x: pos.x, y: pos.y + (depth === 2 ? 22 : 16), w, h, off: depth === 2 ? offsets[4] : offsets[0] };
      }
      if (!placedRect) continue;
      placed.push(placedRect);
      visible.set(p.id, placedRect.off);
    }
    return visible;
  }, [photographers, selected, hovered, activeSet, activeDepths, tweaks.labelDensity, zoom, pan.x, pan.y, viewport.w, viewport.h]);

  // Nebula labels — aggregate movement positions
  const nebulaLabels = useMemo(() => {
    if (mode !== 'nebula') return [];
    const groups = {};
    photographers.forEach((p) => {
      p.movements.forEach((m) => {
        if (!groups[m]) groups[m] = { xs: [], ys: [], count: 0 };
        groups[m].xs.push(p.x);
        groups[m].ys.push(p.y);
        groups[m].count++;
      });
    });
    return Object.entries(groups).
    filter(([, g]) => g.count >= 3).
    map(([move, g]) => ({
      move,
      x: g.xs.reduce((a, b) => a + b, 0) / g.count,
      y: g.ys.reduce((a, b) => a + b, 0) / g.count,
      count: g.count
    }));
  }, [mode, photographers]);

  const showConnections = mode !== 'atlas' || selected;

  // Edge styling based on tweak
  const edgeStyle = tweaks.lineStyle;
  const strokeDash = edgeStyle === 'dashed' ? '3 4' : edgeStyle === 'dotted' ? '1 3' : '0';

  return (
    <div
      ref={stageRef}
      className="stage"
      onPointerDown={onPointerDown}>
      
      {/* Nebula ambient labels (mode-specific) */}
      {mode === 'nebula' && nebulaLabels.map((n) => {
        const px = toPx(n);
        const mv = window.MOVEMENTS[n.move];
        if (!mv) return null;
        return (
          <div
            key={n.move}
            className={`nebula-label ${!selected || activeSet?.has('nothing') ? 'visible' : 'visible'}`}
            style={{
              left: px.x,
              top: px.y,
              color: `oklch(0.8 0.08 ${mv.hue})`
            }}>
            
            {mv.label}
          </div>);

      })}

      <svg>
        {/* Atlas mode: pre-draw faint regional glows */}
        {mode === 'atlas' && nebulaLabels.map((n) => {
          const px = toPx(n);
          const mv = window.MOVEMENTS[n.move];
          if (!mv) return null;
          return (
            <circle
              key={'glow-' + n.move}
              cx={px.x}
              cy={px.y}
              r={60 + n.count * 14}
              fill={`oklch(0.7 0.1 ${mv.hue} / 0.05)`}
              style={{ mixBlendMode: 'screen' }} />);


        })}

        {/* Connections */}
        {showConnections && edges.map((e, i) => {
          const a = byId[e.a];const b = byId[e.b];
          if (!passesFilter(a) && !passesFilter(b)) return null;
          const pa = toPx(a);const pb = toPx(b);
          const connectionLevel = getConnectionLevel(e.a, e.b);
          const isActive = !selected ? false : connectionLevel !== null;
          const shouldDim = selected && !isActive;
          const mv = window.MOVEMENTS[e.move];
          const mvColor = mv ? `oklch(0.84 0.135 ${mv.hue})` : 'var(--accent-cool)';
          if (selected && connectionLevel === null) return null;
          const edgePaint = connectionLevel === 2
            ? { stroke: mvColor, strokeWidth: 1.18, opacity: 0.64 }
            : isActive
              ? { stroke: mvColor, strokeWidth: 1.62, opacity: 0.98 }
              : undefined;

          return (
            <g key={i}>
              <line
                x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y}
                className={`connection ${isActive ? 'active' : ''} ${shouldDim ? 'dim' : ''} ${!selected ? 'idle' : ''}`}
                strokeDasharray={strokeDash}
                style={edgePaint} />
              
            </g>);

        })}

        {/* Stars */}
        {photographers.map((p) => {
          const pos = toPx(p);
          const isActive = p.id === selected;
          const depth = activeDepths?.get(p.id);
          const isNeighbor = depth != null && depth > 0 && !isActive;
          const isHovered = p.id === hovered;
          const isDim = selected && !activeSet.has(p.id) || filter && !passesFilter(p);
          const r = starSize(p);
          const primaryMove = p.movements[0];
          const mv = window.MOVEMENTS[primaryMove];
          const color = mv ? `oklch(${0.75 + p.influence / 50} ${0.05 + p.influence / 100} ${mv.hue})` : '#fff';
          const depthOpacity = depth === 2 ? 0.84 : 1;

          return (
            <g
              key={p.id}
              data-star-id={p.id}
              className={`star ${isActive ? 'active' : ''} ${isHovered ? 'hover' : ''} ${isNeighbor ? 'connected' : ''} ${isDim ? 'dim' : ''}`}
              transform={`translate(${pos.x} ${pos.y})`}
              onMouseEnter={() => onHover(p.id)}
              onMouseLeave={() => onHover(null)}
              style={{ color, opacity: depthOpacity, touchAction: 'none' }}>
              
              {/* Halo */}
              <circle className="star-halo" r={r * 4} fill={color} opacity="0.12" />
              <circle className="star-halo" r={r * 2.2} fill={color} opacity="0.25" />
              {/* Core */}
              <circle
                className="star-core"
                r={r}
                fill={color}
                opacity={tweaks.starBrightness} />
            </g>);

        })}

        {/* Labels — rendered in a second pass so they always sit on top of every star */}
        {photographers.map((p) => {
          const labelOff = labelLayout.get(p.id);
          if (!labelOff) return null;
          const pos = toPx(p);
          const isActive = p.id === selected;
          const isHovered = p.id === hovered;
          const depth = activeDepths?.get(p.id);
          const isNeighbor = depth != null && depth > 0 && !isActive;
          const isDim = selected && !activeSet.has(p.id) || filter && !passesFilter(p);
          // When something is selected, hide labels for unrelated photographers entirely —
          // unless the user is hovering that star, in which case we surface its name.
          if (isDim && !isHovered) return null;
          return (
            <text
              key={'label-' + p.id}
              className={`star-label ${isActive ? 'active' : ''} ${isHovered ? 'hover' : ''} ${isNeighbor ? 'connected' : ''} ${isDim ? 'dim' : ''}`}
              x={pos.x + labelOff.dx}
              y={pos.y + labelOff.dy + (labelOff.dy > 0 ? 4 : -4)}
              textAnchor="middle"
              style={{
                fontSize: isMobileViewport
                  ? isActive ? 11.2 : depth === 1 ? 8.9 : depth === 2 ? 8 : p.influence >= 9 ? 9 : 8.4
                  : isActive ? 13 : depth === 2 ? (p.influence >= 8 ? 9.5 : 8.5) : p.influence >= 8 ? 11.5 : 10.5,
                opacity: isMobileViewport
                  ? isActive ? 0.9 : depth === 1 ? 0.68 : depth === 2 ? 0.48 : 0.54
                  : depth === 2 ? (p.influence >= 8 ? 0.68 : 0.48) : 1
              }}
              pointerEvents="none">
              {labelFor(p)}
            </text>
          );

        })}
      </svg>
    </div>);

}

// ======================================================
// Info Card
// ======================================================
function InfoCard({ selected, isOpen, onToggleOpen, onClose, onSelectRelated, isEnglish = false }) {
  const { byId, adj } = useGraph();
  const nameFor = (p) => isEnglish ? (p.nameEn || p.name || p.nameJa || p.id) : (p.name || p.nameJa || p.nameEn || p.id);
  const altNameFor = (p) => isEnglish ? (p.name || p.nameJa || '') : (p.nameEn || '');
  const movementLabelFor = (m) => isEnglish ? (window.MOVEMENTS_META?.[m]?.en || window.MOVEMENTS?.[m]?.en || m) : m;
  const toggleLabel = selected && byId[selected] ? nameFor(byId[selected]) : (isEnglish ? 'Trace the constellations' : '星座をたどる');
  const toggleSubLabel = selected ? (isEnglish ? 'Photographer' : '作家情報') : 'Guide';
  if (!selected) {
    return (
      <>
        <button className="info-card-toggle" type="button" onClick={onToggleOpen} aria-expanded={isOpen}>
          {toggleSubLabel} · {toggleLabel}
        </button>
        <div className={`info-card ${isOpen ? 'is-open' : ''}`} style={{ width: "223px" }}>
          <div className="card-topline"><span>▸ {isEnglish ? 'Photo Coordinates' : '写真の座標'}</span></div>
          <h2 style={{ fontFamily: "\"DM Mono\"" }}>{isEnglish ? 'Trace the constellations' : '星座をたどる'}</h2>
          <div className="en-name">{isEnglish ? 'Follow the relational field' : 'Trace the constellations'}</div>
          <p style={{ fontSize: 12.5, lineHeight: 1.7, color: 'var(--ink-80)' }}>
            {isEnglish
              ? 'Click a star and the constellation connected by shared photographic contexts appears.'
              : '星をクリックすると、その写真家と同じ表現文脈で繋がる星座が浮かび上がります。'}
          </p>
          <div className="hint">{isEnglish ? 'DRAG explore · CLICK select · context → constellation' : 'DRAG 探索 · CLICK 選択 · 表現の文脈 → 星座'}</div>
        </div>
      </>);

  }
  const p = byId[selected];
  if (!p) return null;
  const detailPath = `${isEnglish ? '/en' : ''}/photographers/${p.id}.html`;
  const detailUrl = (isEnglish ? (p.urlEn || '') : '') || p.url || `https://eyescosmos.github.io${detailPath}`;
  const neighbors = (adj[selected] || []).slice(0, 40);
  // group neighbors by movement
  const byMove = {};
  neighbors.forEach((n) => {
    byMove[n.move] = byMove[n.move] || [];
    if (!byMove[n.move].includes(n.id)) byMove[n.move].push(n.id);
  });

  return (
    <>
      <button className="info-card-toggle" type="button" onClick={onToggleOpen} aria-expanded={isOpen}>
        {toggleSubLabel} · {toggleLabel}
      </button>
      <div className={`info-card ${isOpen ? 'is-open' : ''}`}>
        <button className="close-btn" onClick={onClose} aria-label="close">×</button>
        <div className="card-topline">
          <span>▸ 写真家 / PHOTOGRAPHER</span>
        </div>
        <h2 style={{ fontFamily: isEnglish ? "\"DM Mono\"" : "\"Yu Gothic\"", fontSize: "16px" }}>{nameFor(p)}</h2>
        <div className="en-name">{altNameFor(p)}</div>
        <div className="meta-row">
          <div className="meta">{isEnglish ? 'Years' : '生没年'}<strong>{p.years}</strong></div>
          <div className="meta">{isEnglish ? 'Country' : '国'}<strong>{p.country}</strong></div>
          <div className="meta">{isEnglish ? 'Era' : '年代'}<strong>{p.era}</strong></div>
        </div>
        <div className="movements">
          {p.movements.map((m) => {
            const mv = window.MOVEMENTS[m];
            const color = mv ? `oklch(0.78 0.1 ${mv.hue})` : 'var(--ink-80)';
            return <span key={m} className="movement-chip" style={{ '--chip-color': color }}>{movementLabelFor(m)}</span>;
          })}
        </div>
        <div className="connections-list">
          <strong>{isEnglish ? '★ Connected photographers' : '★ 星座でつながる写真家'}</strong>
          {Object.entries(byMove).map(([move, ids]) => {
            const mv = window.MOVEMENTS[move];
            const color = mv ? `oklch(0.78 0.1 ${mv.hue})` : 'var(--accent-cool)';
            return (
              <div key={move} style={{ marginBottom: 6 }}>
                <span style={{
                  fontFamily: 'var(--font-mono)', fontSize: 9, letterSpacing: '0.15em',
                  color, marginRight: 8, textTransform: 'uppercase'
                }}>{movementLabelFor(move)}</span>
                {ids.map((id, i) =>
                <React.Fragment key={id}>
                    <a onClick={() => onSelectRelated(id)}>{nameFor(byId[id])}</a>
                    {i < ids.length - 1 && <span style={{ color: 'var(--ink-40)' }}>・</span>}
                  </React.Fragment>
                )}
              </div>);

          })}
        </div>
        <a href={detailUrl} target="_blank" rel="noopener" className="hint" style={{ display: 'block', textDecoration: 'none' }}>
          → {isEnglish ? 'Open detail page' : '詳細ページを開く'} / {detailUrl.replace('https://eyescosmos.github.io', '')}
        </a>
      </div>
    </>);

}

// ======================================================
// Mode Switcher
// ======================================================
function ModeSwitcher({ mode, onChange }) {
  const modes = [
  { id: 'constellation', label: 'CONSTELLATION' },
  { id: 'nebula', label: 'NEBULA' },
  { id: 'atlas', label: 'ATLAS' }];

  return (
    <div className="mode-switcher">
      {modes.map((m) =>
      <button
        key={m.id}
        className={mode === m.id ? 'active' : ''}
        onClick={() => onChange(m.id)}>
        {m.label}</button>
      )}
    </div>);

}

// ======================================================
// Dropdown (movement / country / era filter)
// ======================================================
function FilterDropdown({ label, options, filter, onChange, kind }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    const onDoc = (e) => {if (!ref.current?.contains(e.target)) setOpen(false);};
    document.addEventListener('click', onDoc);
    return () => document.removeEventListener('click', onDoc);
  }, []);
  const active = filter?.type === kind ? filter.value : null;
  return (
    <div className="dropdown" ref={ref}>
      <button className="dropdown-btn" onClick={() => setOpen(!open)} style={{ width: "159px", height: "40px" }}>
        <span>{active || label}</span>
        <span className="chev">▼</span>
      </button>
      {open &&
      <div className="dropdown-menu">
          <button onClick={() => {onChange(null);setOpen(false);}}>— すべて —</button>
          {options.map((o) =>
        <button
          key={o}
          className={active === o ? 'active' : ''}
          onClick={() => {onChange({ type: kind, value: o });setOpen(false);}}>
          {o}</button>
        )}
        </div>
      }
    </div>);

}

// ======================================================
// Tweaks Panel
// ======================================================
function ConnectionLegend({ selected, hops = 2, isEnglish = false }) {
  const { byId, adj } = useGraph();
  const movementLabelFor = (m) => isEnglish ? (window.MOVEMENTS_META?.[m]?.en || window.MOVEMENTS?.[m]?.en || m) : m;
  const [legendOpen, setLegendOpen] = useState(() => {
    try {
      return window.innerWidth > 768;
    } catch {
      return true;
    }
  });
  if (!selected || !byId[selected]) return null;
  const depths = new Map([[selected, 0]]);
  let frontier = [selected];
  for (let h = 0; h < hops; h += 1) {
    const next = [];
    frontier.forEach((id) => {
      (adj[id] || []).forEach((n) => {
        if (!depths.has(n.id)) {
          depths.set(n.id, h + 1);
          next.push(n.id);
        }
      });
    });
    frontier = next;
    if (!frontier.length) break;
  }

  const moveMeta = new Map();
  (window.CONNECTIONS || []).forEach(([a, b, m]) => {
    const aDepth = depths.get(a);
    const bDepth = depths.get(b);
    if (aDepth == null || bDepth == null) return;
    const low = Math.min(aDepth, bDepth);
    const high = Math.max(aDepth, bDepth);
    if (!((low === 0 && high === 1) || (low === 1 && high === 2))) return;
    const prev = moveMeta.get(m);
    if (!prev) {
      moveMeta.set(m, { minLevel: high, count: 1 });
    } else {
      prev.minLevel = Math.min(prev.minLevel, high);
      prev.count += 1;
    }
  });

  const moves = Array.from(moveMeta.entries())
    .sort((a, b) => {
      if (a[1].minLevel !== b[1].minLevel) return a[1].minLevel - b[1].minLevel;
      if (a[1].count !== b[1].count) return b[1].count - a[1].count;
      return a[0].localeCompare(b[0], 'ja');
    })
    .map(([move]) => move);
  if (moves.length === 0) return null;
  return (
    <details className="connection-legend" open={legendOpen} onToggle={(event) => setLegendOpen(event.currentTarget.open)}>
      <summary className="legend-summary">{isEnglish ? 'Lines' : '線'}</summary>
      <div className="legend-title">{isEnglish ? 'Line color = shared context' : '線の色 = 表現でのつながり'}</div>
      <ul>
        {moves.map((m) => {
          const mv = window.MOVEMENTS[m];
          if (!mv) return null;
          const color = `oklch(0.84 0.135 ${mv.hue})`;
          return (
            <li key={m}>
              <span className="legend-swatch" style={{ background: color, boxShadow: `0 0 9px ${color}` }} />
              <span className="legend-label">{movementLabelFor(m)}</span>
            </li>);

        })}
      </ul>
    </details>);

}

function TweaksPanel({ tweaks, onChange, visible }) {
  if (!visible) return null;
  const update = (k, v) => onChange({ ...tweaks, [k]: v });
  return (
    <div className="tweaks-panel">
      <h3>Tweaks</h3>

      <div className="tweak">
        <label>Background 背景</label>
        <div className="seg-group">
          <button className={tweaks.theme === 'dark' ? 'active' : ''} onClick={() => update('theme', 'dark')}>星空</button>
          <button className={tweaks.theme === 'flat' ? 'active' : ''} onClick={() => update('theme', 'flat')}>無地</button>
          <button className={tweaks.theme === 'light' ? 'active' : ''} onClick={() => update('theme', 'light')}>LIGHT</button>
        </div>
      </div>

      <div className="tweak">
        <label>Line Opacity 接続線の濃さ</label>
        <input type="range" min="0" max="0.6" step="0.01" value={tweaks.lineOpacity}
        onChange={(e) => update('lineOpacity', parseFloat(e.target.value))} />
        <div className="value-readout">{Math.round(tweaks.lineOpacity * 100)}%</div>
      </div>

      <div className="tweak">
        <label>Star Size 星のサイズ</label>
        <input type="range" min="1" max="6" step="0.1" value={tweaks.starSize}
        onChange={(e) => update('starSize', parseFloat(e.target.value))} />
        <div className="value-readout">{tweaks.starSize.toFixed(1)}×</div>
      </div>

      <div className="tweak">
        <label>Star Brightness 明るさ</label>
        <input type="range" min="0.3" max="1" step="0.05" value={tweaks.starBrightness}
        onChange={(e) => update('starBrightness', parseFloat(e.target.value))} />
        <div className="value-readout">{Math.round(tweaks.starBrightness * 100)}%</div>
      </div>

      <div className="tweak">
        <label>Labels ラベル表示</label>
        <div className="seg-group">
          <button className={tweaks.labelDensity === 'minimal' ? 'active' : ''} onClick={() => update('labelDensity', 'minimal')}>最小</button>
          <button className={tweaks.labelDensity === 'important' ? 'active' : ''} onClick={() => update('labelDensity', 'important')}>重要</button>
          <button className={tweaks.labelDensity === 'all' ? 'active' : ''} onClick={() => update('labelDensity', 'all')}>全表示</button>
        </div>
      </div>

      <div className="tweak">
        <label>Hops つながりの深さ</label>
        <div className="seg-group">
          <button className={tweaks.hops === 1 ? 'active' : ''} onClick={() => update('hops', 1)}>1世代</button>
          <button className={tweaks.hops === 2 ? 'active' : ''} onClick={() => update('hops', 2)}>2世代</button>
        </div>
      </div>

      <div className="tweak">
        <label>Connection Line 接続線</label>
        <div className="seg-group">
          <button className={tweaks.lineStyle === 'solid' ? 'active' : ''} onClick={() => update('lineStyle', 'solid')}>SOLID</button>
          <button className={tweaks.lineStyle === 'dashed' ? 'active' : ''} onClick={() => update('lineStyle', 'dashed')}>DASH</button>
          <button className={tweaks.lineStyle === 'dotted' ? 'active' : ''} onClick={() => update('lineStyle', 'dotted')}>DOT</button>
        </div>
      </div>

      <div className="tweak">
        <label>Typography フォント</label>
        <div className="seg-group">
          <button className={tweaks.font === 'serif' ? 'active' : ''} onClick={() => update('font', 'serif')}>SERIF</button>
          <button className={tweaks.font === 'sans' ? 'active' : ''} onClick={() => update('font', 'sans')}>SANS</button>
          <button className={tweaks.font === 'mixed' ? 'active' : ''} onClick={() => update('font', 'mixed')}>MIXED</button>
        </div>
      </div>
    </div>);

}

// ======================================================
// Root App
// ======================================================
const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "theme": "dark",
  "starSize": 2.6,
  "starBrightness": 0.92,
  "labelDensity": "important",
  "lineStyle": "solid",
  "font": "mixed",
  "hops": 2,
  "spread": 2.1,
  "lineOpacity": 0.025,
  "mode": "constellation"
} /*EDITMODE-END*/;

const MOBILE_TOP_CSS = `
.info-card-toggle {
  display: none;
}
.connection-legend .legend-summary {
  display: none;
  list-style: none;
}
.connection-legend .legend-summary::-webkit-details-marker {
  display: none;
}
.mobile-label-toggle {
  display: none;
}
html, body, #root, .app, .stage, .stage svg, .star-label, .connection-label, .nebula-label {
  user-select: none;
  -webkit-user-select: none;
}
input, textarea, select {
  user-select: text;
  -webkit-user-select: text;
}
@media (max-width: 699px) {
  html, body, #root, .app {
    overscroll-behavior: none;
    touch-action: none;
  }
  .stage,
  .stage svg {
    touch-action: none;
    user-select: none;
    -webkit-user-select: none;
  }
  .masthead {
    top: calc(16px + env(safe-area-inset-top, 0px));
    left: 16px;
    max-width: 220px;
  }
  .masthead.dim {
    opacity: 0.72;
  }
  .masthead .eyebrow {
    margin-bottom: 8px;
    font-size: 9px;
    letter-spacing: 0.16em;
  }
  .masthead h1 {
    font-size: 40px;
    margin-bottom: 6px;
  }
  .masthead .sub-en {
    display: none;
    margin-bottom: 0;
    font-size: 9px;
    letter-spacing: 0.2em;
  }
  .masthead p {
    display: none;
  }
  .side-controls {
    top: calc(16px + env(safe-area-inset-top, 0px));
    right: 16px;
    gap: 0;
    align-items: flex-end;
  }
  .side-controls .dropdown {
    display: none;
  }
  .lang-toggle {
    margin-bottom: 0;
  }
  .lang-toggle button {
    min-width: 44px;
    padding: 7px 10px;
    font-size: 10px;
  }
  .mobile-label-toggle {
    display: block;
    width: 92px;
    min-height: 24px;
    margin-top: 3px;
    border: 1px solid var(--ink-20);
    border-radius: 2px;
    background: rgba(10, 14, 24, 0.54);
    color: var(--ink-60);
    font: 400 8px/1 var(--font-mono);
    letter-spacing: 0.08em;
    cursor: pointer;
  }
  .mobile-label-toggle.active {
    background: var(--ink-100);
    color: var(--bg-0);
  }
  .side-controls .spread-control {
    position: fixed;
    top: calc(84px + env(safe-area-inset-top, 0px));
    left: 20px;
    z-index: 24;
    width: 18px !important;
    height: 118px;
    min-width: 0;
    padding: 0;
    border: 0;
    background: transparent;
    backdrop-filter: none;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .side-controls .spread-control input[type="range"] {
    width: 118px;
    height: 2px;
    transform: rotate(-90deg);
    transform-origin: center;
  }
  .side-controls .spread-control input[type="range"]::-webkit-slider-thumb {
    width: 11px;
    height: 11px;
  }
  .side-controls .spread-control input[type="range"]::-moz-range-thumb {
    width: 11px;
    height: 11px;
  }
  .info-card {
    display: none !important;
  }
  .info-card.is-open {
    display: block !important;
    left: 16px !important;
    right: 16px !important;
    bottom: calc(64px + env(safe-area-inset-bottom, 0px)) !important;
    width: auto !important;
    max-height: min(52svh, 360px) !important;
    padding: 16px 18px !important;
  }
  .info-card-toggle {
    display: block;
    position: absolute;
    left: 16px;
    bottom: calc(16px + env(safe-area-inset-bottom, 0px));
    z-index: 22;
    min-width: 132px;
    max-width: calc(100vw - 152px);
    min-height: 34px;
    padding: 8px 12px;
    border: 1px solid var(--ink-20);
    border-radius: 2px;
    background: rgba(10, 14, 24, 0.78);
    color: var(--ink-80);
    font: 400 10px/1.2 var(--font-mono);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    backdrop-filter: blur(12px);
  }
  .connection-legend {
    display: block !important;
    top: calc(76px + env(safe-area-inset-top, 0px)) !important;
    right: 16px !important;
    bottom: auto !important;
    width: 92px !important;
    max-height: min(34svh, 230px) !important;
    padding: 0 !important;
    overflow: hidden !important;
  }
  .connection-legend .legend-summary {
    display: block;
    min-height: 24px;
    padding: 7px 8px;
    color: var(--ink-80);
    font: 400 9px/1.1 var(--font-mono);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    cursor: pointer;
  }
  .connection-legend .legend-summary::after {
    content: '+';
    float: right;
    color: var(--ink-40);
  }
  .connection-legend[open] .legend-summary::after {
    content: '×';
  }
  .connection-legend .legend-title {
    padding: 0 8px 5px;
    margin: 0;
    font-size: 8px;
    letter-spacing: 0.1em;
  }
  .connection-legend ul {
    padding: 0 8px 8px !important;
    gap: 2px !important;
  }
  .connection-legend li {
    gap: 5px !important;
    font-size: 8px !important;
    line-height: 1.25 !important;
  }
  .connection-legend .legend-swatch {
    width: 9px !important;
  }
}
`;

function App() {
  const [selected, setSelected] = useState(null);
  const [hovered, setHovered] = useState(null);
  const [mode, setMode] = useState(TWEAK_DEFAULTS.mode);
  const [filter, setFilter] = useState(null);
  const [tweaks, setTweaks] = useState(() => {
    try {
      return isMobileViewportWidth(window.innerWidth)
        ? { ...TWEAK_DEFAULTS, spread: 3.2, labelDensity: 'minimal' }
        : TWEAK_DEFAULTS;
    } catch {
      return TWEAK_DEFAULTS;
    }
  });
  const [showTweaks, setShowTweaks] = useState(false);
  const [editModeHost, setEditModeHost] = useState(false);
  const [infoCardOpen, setInfoCardOpen] = useState(false);
  const [mobileShowAllNames, setMobileShowAllNames] = useState(false);

  // Restore persisted selection
  useEffect(() => {
    try {
      const saved = localStorage.getItem('pc_selected');
      if (saved) setSelected(saved);
      const m = localStorage.getItem('pc_mode');
      if (m) setMode(m);
    } catch {}
  }, []);
  useEffect(() => {
    try {
      if (selected) localStorage.setItem('pc_selected', selected);else
      localStorage.removeItem('pc_selected');
    } catch {}
  }, [selected]);
  useEffect(() => {
    setInfoCardOpen(false);
  }, [selected]);
  useEffect(() => {
    try {localStorage.setItem('pc_mode', mode);} catch {}
  }, [mode]);

  // Edit mode host handshake
  useEffect(() => {
    const onMsg = (e) => {
      const d = e.data;
      if (!d || typeof d !== 'object') return;
      if (d.type === '__activate_edit_mode') setEditModeHost(true);
      if (d.type === '__deactivate_edit_mode') setEditModeHost(false);
      if (d.type === '__pc_reset_selection') {
        setSelected(null);
        setInfoCardOpen(false);
      }
      if (d.type === '__pc_select_photographer') {
        const id = String(d.id || '').replace(/^photographer:/, '');
        const exists = (window.PHOTOGRAPHERS || []).some((p) => p && p.id === id);
        if (exists) {
          setSelected(id);
          setInfoCardOpen(true);
        }
      }
    };
    window.addEventListener('message', onMsg);
    window.parent?.postMessage({ type: '__edit_mode_available' }, '*');
    return () => window.removeEventListener('message', onMsg);
  }, []);

  // Persist tweaks via edit-mode keys
  const updateTweaks = useCallback((next) => {
    setTweaks(next);
    window.parent?.postMessage({ type: '__edit_mode_set_keys', edits: next }, '*');
  }, []);

  const openPhotographerPage = useCallback((id) => {
    const currentPath = (() => {
      try {
        if (window.parent && window.parent !== window) return window.parent.location.pathname || '';
      } catch {}
      return window.location.pathname || '';
    })();
    const langPrefix = /(^|\/)en(\/|$)/.test(currentPath) ? '/en' : '';
    const href = `${langPrefix}/photographers/${id}.html`;
    try {
      if (window.parent && window.parent !== window) {
        window.parent.location.href = href;
        return;
      }
    } catch {}
    window.location.href = href;
  }, []);

  const handleSelect = useCallback((id) => {
    if (id === selected) {
      openPhotographerPage(id);
      return;
    }
    setSelected(id);
    setInfoCardOpen(false);
  }, [openPhotographerPage, selected]);

  // Keep tweak panel visible only when host is in edit mode (Tweaks toolbar toggle on).
  // The standalone bundled HTML never receives that message, so Tweaks stays hidden.
  const tweaksVisible = editModeHost;

  // Derived filter options
  const movements = useMemo(() => {
    const s = new Set();
    window.PHOTOGRAPHERS.forEach((p) => p.movements.forEach((m) => s.add(m)));
    return Array.from(s).sort();
  }, []);
  const countries = useMemo(() => {
    const s = new Set();
    window.PHOTOGRAPHERS.forEach((p) => s.add(p.country));
    return Array.from(s).sort();
  }, []);
  const eras = useMemo(() => {
    const s = new Set();
    window.PHOTOGRAPHERS.forEach((p) => s.add(p.era));
    return Array.from(s).sort();
  }, []);

  // Font class
  const fontClass = tweaks.font === 'sans' ? 'font-sans' : tweaks.font === 'serif' ? 'font-serif' : 'font-mixed';
  const isMobileApp = (() => {
    try {
      return isMobileViewportWidth(window.innerWidth);
    } catch {
      return false;
    }
  })();
  const isEnglishApp = (() => {
    try {
      const parentPath = window.parent && window.parent !== window ? window.parent.location.pathname : window.location.pathname;
      return /(^|\/)en(\/|$)/.test(parentPath || '');
    } catch {
      return /(^|\/)en(\/|$)/.test(window.location.pathname || '');
    }
  })();
  const constellationTweaks = mobileShowAllNames
    ? { ...tweaks, labelDensity: 'all' }
    : tweaks;

  return (
    <div
      className={`app theme-${tweaks.theme} ${fontClass}`}
      style={{
        '--connection-opacity': tweaks.lineOpacity,
        ...(tweaks.font === 'sans' ? { fontFamily: 'var(--font-sans)' } :
        tweaks.font === 'serif' ? { fontFamily: 'var(--font-serif)' } : {})
      }}>
      <style>{MOBILE_TOP_CSS}</style>
      
      {tweaks.theme === 'dark' && <Starfield density={window.innerWidth < 700 ? 160 : 300} theme="dark" />}
      {tweaks.theme === 'light' && <Starfield density={120} theme="light" />}

      <Constellation
        mode={mode}
        selected={selected}
        onSelect={handleSelect}
        hovered={hovered}
        onHover={setHovered}
        tweaks={constellationTweaks}
        filter={filter}
        isEnglish={isEnglishApp} />
      

      {/* Masthead */}
      <div className={`masthead ${selected ? 'dim' : ''}`}>
        <div className="eyebrow">
          PHOTO COORDINATES
        </div>
        <h1>写真の座標</h1>
        <div className="sub-en">PHOTO · COORDINATES</div>
        <p>
          {isEnglishApp
            ? 'An archive for tracing photographers through shared visual contexts. Tap a star to reveal its constellation.'
            : '世界の写真家を〈表現の文脈〉で結び、星座のように辿るアーカイブ。星をタップすると同じ運動・技法で結ばれた星座が浮かび上がります。'}
        </p>
      </div>

      {editModeHost && <ModeSwitcher mode={mode} onChange={setMode} />}

      <div className="side-controls">
        <div className="lang-toggle">
          <button className="active">JP</button>
          <button>EN</button>
        </div>
        <button
          className={`mobile-label-toggle ${mobileShowAllNames ? 'active' : ''}`}
          type="button"
          onClick={() => setMobileShowAllNames((show) => !show)}
          aria-pressed={mobileShowAllNames}>
          {isEnglishApp ? 'Show names' : '作家名表示'}
        </button>
        <FilterDropdown label={isEnglishApp ? 'Browse movements' : '表現から見る'} kind="movement" options={movements} filter={filter} onChange={setFilter} />
        <FilterDropdown label={isEnglishApp ? 'Browse countries' : '国別で見る'} kind="country" options={countries} filter={filter} onChange={setFilter} />
        <FilterDropdown label={isEnglishApp ? 'Browse eras' : '年代でみる'} kind="era" options={eras} filter={filter} onChange={setFilter} />
        <div className="spread-control" style={{ width: "159px" }}>
          <input
            type="range"
            min={isMobileApp ? "2.2" : "0.6"} max={isMobileApp ? "4.2" : "3.2"} step="0.05"
            value={tweaks.spread}
            onChange={(e) => updateTweaks({ ...tweaks, spread: parseFloat(e.target.value) })}
            aria-label="星の散らばり" />
          
        </div>
      </div>

      <InfoCard
        selected={selected}
        isOpen={infoCardOpen}
        onToggleOpen={() => setInfoCardOpen((open) => !open)}
        onClose={() => setInfoCardOpen(false)}
        onSelectRelated={(id) => {
          setSelected(id);
          setInfoCardOpen(false);
        }}
        isEnglish={isEnglishApp} />
      

      <ConnectionLegend selected={selected} hops={tweaks.hops} isEnglish={isEnglishApp} />

      {editModeHost && (
        <div className="action-buttons">
          <button title="Tweaks" onClick={() => setShowTweaks(!showTweaks)} aria-label="tweaks">◎</button>
          <button title="About" aria-label="about">i</button>
        </div>
      )}

      <TweaksPanel tweaks={tweaks} onChange={updateTweaks} visible={tweaksVisible} />

      <a href="#" className="footer-link">プライバシーポリシー</a>
    </div>);

}

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
