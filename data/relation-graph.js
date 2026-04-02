(function () {
  const photographersSource =
    typeof PHOTOGRAPHERS !== 'undefined'
      ? PHOTOGRAPHERS
      : (window.PHOTOGRAPHERS || []);
  const movementMetaSource =
    typeof MOVEMENTS_META !== 'undefined'
      ? MOVEMENTS_META
      : (window.MOVEMENTS_META || {});

  const photographers = photographersSource.filter(p => !p.isPlaceholder);
  const photographerOrder = new Map(photographers.map((p, index) => [p.id, index]));
  const movementMeta = Object.assign({}, movementMetaSource, {
    'LGBTQ+': {
      en: 'LGBTQ+ Photography',
      desc: '性的マイノリティの経験や共同体、身体の表象をめぐる写真実践。'
    },
    'イギリス写真': {
      en: 'British Photography',
      desc: '戦後イギリスの階級・消費・日常文化を批評的に見つめる写真実践。'
    },
    'コンセプチュアルアート': {
      en: 'Conceptual Art',
      desc: '作品の物質性よりも、概念や制度批評を前景化する美術的文脈。'
    },
    'シネマトグラフィック写真': {
      en: 'Cinematographic Photography',
      desc: '映画的な構図、時間感覚、舞台性を写真の中に持ち込む表現。'
    },
    'ステージド写真': {
      en: 'Staged Photography',
      desc: '現実をそのまま記録するのではなく、演出された場面を構築する写真。'
    },
    'タイポロジー写真': {
      en: 'Typological Photography',
      desc: '対象を同一条件で反復撮影し、差異と構造を比較可能にする写真。'
    },
    'デュッセルドルフ派': {
      en: 'Dusseldorf School',
      desc: 'ベルント＆ヒラ・ベッヒャーの教育を軸に展開した、構造的で大判的な写真の潮流。'
    },
    'ニューカラー': {
      en: 'New Color',
      desc: '色彩そのものを写真の意味生成に積極的に組み込んだ1970年代以降の流れ。'
    },
    'プライベート写真': {
      en: 'Private Photography',
      desc: '親密圏や日常の断片を、個人的記録と表現の境界で扱う写真。'
    },
    '大判カラー写真': {
      en: 'Large-Format Color',
      desc: '大判カメラと色彩を通じて現代社会の構造やスケール感を描く実践。'
    },
    '環境写真': {
      en: 'Environmental Photography',
      desc: '自然環境や労働環境の変容を、社会的・地球規模の問題として捉える写真。'
    },
    '社会的写真': {
      en: 'Social Photography',
      desc: '社会構造や格差、共同体の問題を批評的に扱う写真の実践。'
    }
  });

  const eraOrder = ['1839', '1870', '1890', '1910', '1930', '1950', '1970', '1980'];
  const eraLabels = {
    '1839': '1839–1860s',
    '1870': '1870–1890s',
    '1890': '1890–1900s',
    '1910': '1910–1920s',
    '1930': '1930–1940s',
    '1950': '1950–1960s',
    '1970': '1970s',
    '1980': '1980s'
  };

  const ideas = [
    { id: 'idea:machine-eye', label: '機械の眼', subtitle: 'apparatus / optics', type: 'idea' },
    { id: 'idea:portrait-self', label: '肖像と自己', subtitle: 'identity / body', type: 'idea' },
    { id: 'idea:city-street', label: '都市を歩く視線', subtitle: 'street / city', type: 'idea' },
    { id: 'idea:experiment', label: '実験と抽象', subtitle: 'experiment / abstraction', type: 'idea' },
    { id: 'idea:staged-image', label: '演出されたイメージ', subtitle: 'staged / cinematic', type: 'idea' },
    { id: 'idea:system', label: '類型とシステム', subtitle: 'typology / structure', type: 'idea' },
    { id: 'idea:color', label: '色彩と日常', subtitle: 'color / everyday', type: 'idea' },
    { id: 'idea:intimacy', label: '私性と記憶', subtitle: 'intimacy / memory', type: 'idea' },
    { id: 'idea:critique', label: '政治と批評', subtitle: 'critique / representation', type: 'idea' },
    { id: 'idea:landscape', label: '空間と風景', subtitle: 'landscape / environment', type: 'idea' }
  ];

  const featuredMovements = new Set([
    'ドキュメンタリー',
    '戦争写真',
    'ピクトリアリズム',
    'ストレート写真',
    'ストリート写真',
    'モダニズム',
    'シュルレアリスム',
    'コンセプチュアル',
    '写真分離派',
    'ダダ',
    'レイオグラフ',
    'バウハウス',
    '新しいヴィジョン',
    '新即物主義',
    'ヴォルテクシズム',
    'フォトジャーナリズム',
    '決定的瞬間',
    'リアリズム写真',
    '日本写真',
    'プロヴォーク',
    'アメリカ写真',
    'ピクチャーズ世代',
    'フェミニズム写真',
    'デュッセルドルフ派',
    'コンセプチュアルアート',
    'ニューカラー',
    'タイポロジー写真',
    '私写真',
    '自然主義写真'
  ]);

  const featuredIdeaIds = new Set([
    'idea:machine-eye'
  ]);

  const movementIdeaMap = {
    '発明・技術': ['idea:machine-eye', 'idea:experiment'],
    'ドキュメンタリー': ['idea:city-street', 'idea:critique'],
    '戦争写真': ['idea:critique', 'idea:city-street'],
    '植民地写真': ['idea:critique', 'idea:city-street'],
    'ポートレート': ['idea:portrait-self'],
    '風景写真': ['idea:landscape', 'idea:machine-eye'],
    'ピクトリアリズム': ['idea:experiment', 'idea:portrait-self'],
    'ストレート写真': ['idea:machine-eye', 'idea:city-street'],
    'ストリート写真': ['idea:city-street', 'idea:critique'],
    '社会ドキュメンタリー': ['idea:critique', 'idea:city-street'],
    'モダニズム': ['idea:experiment', 'idea:machine-eye'],
    'シュルレアリスム': ['idea:experiment', 'idea:portrait-self'],
    'カラー写真': ['idea:color', 'idea:landscape'],
    'コンセプチュアル': ['idea:staged-image', 'idea:critique'],
    '科学写真': ['idea:machine-eye', 'idea:experiment'],
    '実験的技法': ['idea:machine-eye', 'idea:experiment'],
    '自然主義写真': ['idea:landscape', 'idea:machine-eye'],
    '都市記録': ['idea:city-street', 'idea:critique'],
    '写真分離派': ['idea:experiment', 'idea:portrait-self'],
    'ダダ': ['idea:experiment', 'idea:critique'],
    'レイオグラフ': ['idea:experiment', 'idea:machine-eye'],
    'バウハウス': ['idea:experiment', 'idea:machine-eye'],
    '新しいヴィジョン': ['idea:experiment', 'idea:machine-eye'],
    '新即物主義': ['idea:system', 'idea:machine-eye'],
    'ヴォルテクシズム': ['idea:experiment', 'idea:machine-eye'],
    'FSA写真': ['idea:critique', 'idea:city-street'],
    'フォトジャーナリズム': ['idea:critique', 'idea:city-street'],
    '決定的瞬間': ['idea:city-street', 'idea:machine-eye'],
    'リアリズム写真': ['idea:critique', 'idea:city-street'],
    '私写真': ['idea:intimacy', 'idea:portrait-self'],
    '日本写真': ['idea:city-street', 'idea:critique'],
    'プロヴォーク': ['idea:city-street', 'idea:critique'],
    'アメリカ写真': ['idea:city-street', 'idea:color'],
    'ピクチャーズ世代': ['idea:critique', 'idea:staged-image'],
    'フェミニズム写真': ['idea:portrait-self', 'idea:critique'],
    'LGBTQ+': ['idea:intimacy', 'idea:portrait-self'],
    'イギリス写真': ['idea:city-street', 'idea:critique'],
    'コンセプチュアルアート': ['idea:staged-image', 'idea:critique'],
    'シネマトグラフィック写真': ['idea:staged-image', 'idea:color'],
    'ステージド写真': ['idea:staged-image', 'idea:critique'],
    'タイポロジー写真': ['idea:system', 'idea:machine-eye'],
    'デュッセルドルフ派': ['idea:system', 'idea:landscape'],
    'ニューカラー': ['idea:color', 'idea:city-street'],
    'プライベート写真': ['idea:intimacy', 'idea:portrait-self'],
    '大判カラー写真': ['idea:color', 'idea:system'],
    '環境写真': ['idea:landscape', 'idea:critique'],
    '社会的写真': ['idea:critique', 'idea:city-street']
  };

  const movementRelations = [
    ['発明・技術', '科学写真'],
    ['科学写真', '実験的技法'],
    ['実験的技法', 'モダニズム'],
    ['モダニズム', 'バウハウス'],
    ['バウハウス', '新しいヴィジョン'],
    ['ダダ', 'シュルレアリスム'],
    ['レイオグラフ', 'シュルレアリスム'],
    ['ピクトリアリズム', '写真分離派'],
    ['写真分離派', 'ストレート写真'],
    ['ストレート写真', 'モダニズム'],
    ['ドキュメンタリー', '社会ドキュメンタリー'],
    ['社会ドキュメンタリー', 'FSA写真'],
    ['FSA写真', 'フォトジャーナリズム'],
    ['フォトジャーナリズム', '決定的瞬間'],
    ['決定的瞬間', 'ストリート写真'],
    ['都市記録', 'ストリート写真'],
    ['リアリズム写真', '日本写真'],
    ['日本写真', 'プロヴォーク'],
    ['プロヴォーク', '私写真'],
    ['私写真', 'プライベート写真'],
    ['アメリカ写真', 'ニューカラー'],
    ['カラー写真', 'ニューカラー'],
    ['ニューカラー', '大判カラー写真'],
    ['大判カラー写真', '環境写真'],
    ['新即物主義', 'タイポロジー写真'],
    ['タイポロジー写真', 'デュッセルドルフ派'],
    ['コンセプチュアル', 'ピクチャーズ世代'],
    ['ピクチャーズ世代', 'コンセプチュアルアート'],
    ['コンセプチュアルアート', 'ステージド写真'],
    ['ステージド写真', 'シネマトグラフィック写真'],
    ['フェミニズム写真', 'LGBTQ+'],
    ['社会ドキュメンタリー', '社会的写真'],
    ['社会的写真', '環境写真'],
    ['ストリート写真', 'イギリス写真']
  ];

  function movementSlug(name) {
    return name.replace(/[^a-zA-Z\u3000-\u9fff]/g, '');
  }

  function pushUniqueLink(target, seen, source, destination, type) {
    const key = [source, destination].sort().join('::');
    if (seen.has(key)) return;
    seen.add(key);
    target.push({ source, target: destination, type });
  }

  function eraIndex(eraId) {
    const index = eraOrder.indexOf(eraId);
    return index >= 0 ? index : eraOrder.length;
  }

  const usedMovements = Array.from(
    new Set(
      photographers
        .flatMap(p => p.movements || [])
        .filter(name => name && featuredMovements.has(name))
    )
  ).sort((a, b) => a.localeCompare(b, 'ja'));

  const featuredPhotographerIds = new Set([
    'stieglitz',
    'strand',
    'atget',
    'manray',
    'evans',
    'capa',
    'domon',
    'araki',
    'frank',
    'becher'
  ]);

  const photographerNodes = photographers.map((p, index) => ({
    id: `photographer:${p.id}`,
    key: p.id,
    label: p.nameJa || p.name,
    subtitle: [p.name, p.years].filter(Boolean).join(' / '),
    type: 'photographer',
    era: p.era,
    years: p.years,
    order: index,
    prominence: featuredPhotographerIds.has(p.id) ? 1 : 0,
    url: `archive.html#photographer-${p.id}`
  }));

  const movementNodes = usedMovements.map(name => {
    const meta = movementMeta[name] || { en: name, desc: '' };
    return {
      id: `movement:${name}`,
      key: name,
      label: name,
      subtitle: meta.en || '',
      description: meta.desc || '',
      type: 'movement',
      url: `archive.html#movement-${movementSlug(name)}`
    };
  });

  const usedIdeaIds = new Set();
  usedMovements.forEach(name => {
    (movementIdeaMap[name] || []).forEach(ideaId => {
      if (featuredIdeaIds.has(ideaId)) {
        usedIdeaIds.add(ideaId);
      }
    });
  });

  const ideaNodes = ideas.filter(idea => usedIdeaIds.has(idea.id));
  const nodes = [...photographerNodes, ...movementNodes, ...ideaNodes];
  const links = [];
  const seenLinks = new Set();

  photographers.forEach(p => {
    const photographerId = `photographer:${p.id}`;
    (p.movements || []).forEach(name => {
      if (usedMovements.includes(name)) {
        pushUniqueLink(links, seenLinks, photographerId, `movement:${name}`, 'belongs_to');
      }
    });
  });

  usedMovements.forEach(name => {
    const relatedPhotographers = photographers
      .filter(p => (p.movements || []).includes(name))
      .sort((a, b) => {
        const eraDiff = eraIndex(a.era) - eraIndex(b.era);
        if (eraDiff !== 0) return eraDiff;
        return (photographerOrder.get(a.id) || 0) - (photographerOrder.get(b.id) || 0);
      });

    for (let i = 1; i < relatedPhotographers.length; i += 1) {
      pushUniqueLink(
        links,
        seenLinks,
        `photographer:${relatedPhotographers[i - 1].id}`,
        `photographer:${relatedPhotographers[i].id}`,
        'movement_peer'
      );
    }
  });

  movementRelations.forEach(([source, destination]) => {
    if (!usedMovements.includes(source) || !usedMovements.includes(destination)) return;
    pushUniqueLink(links, seenLinks, `movement:${source}`, `movement:${destination}`, 'influences');
  });

  usedMovements.forEach(name => {
    const relatedIdeas = (movementIdeaMap[name] || ['idea:critique'])
      .filter(ideaId => featuredIdeaIds.has(ideaId));
    relatedIdeas.forEach(ideaId => {
      pushUniqueLink(links, seenLinks, `movement:${name}`, ideaId, 'idea');
    });
  });

  const eraPhotographers = new Map();
  photographers.forEach(p => {
    const list = eraPhotographers.get(p.era) || [];
    list.push(p);
    eraPhotographers.set(p.era, list);
  });

  eraOrder.forEach(eraId => {
    const list = eraPhotographers.get(eraId) || [];
    for (let i = 1; i < list.length; i += 1) {
      pushUniqueLink(
        links,
        seenLinks,
        `photographer:${list[i - 1].id}`,
        `photographer:${list[i].id}`,
        'era'
      );
    }
  });

  window.RELATION_GRAPH = {
    nodes,
    links,
    movementMeta,
    eras: eraOrder.map(id => ({ id, label: eraLabels[id] || id }))
  };
})();
