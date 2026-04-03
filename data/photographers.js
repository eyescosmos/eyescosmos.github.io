const PHOTOGRAPHERS = [
  /* ─────────────────────────────────────────
     1839–1860s
     ───────────────────────────────────────── */
  {
    id: 'daguerre',
    name: 'Louis Daguerre',
    nameJa: 'ルイ・ダゲール',
    nationality: 'FR',
    flag: '🇫🇷',
    years: '1787–1851',
    gender: '男性',
    era: '1839',
    movements: ['発明・技術'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/essays/daguerre-1787-1851-and-the-invention-of-photography' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Louis_Daguerre' },
    ],
    amazon: '',
    context: {
      text: 'ダゲールはパリで大型ジオラマ劇場を経営する舞台演出家だった。ジオラマは透過光と反射光を切り替えて風景画を昼から夜へと変化させる視覚装置であり、光と像の定着への強い関心をもたらした*1。1826年頃から発明家ニエプスと共同研究を開始し、ニエプスの死後（1833年）も銀板に水銀蒸気で像を定着させる方法を独自に改良し続けた。1839年1月7日、フランス科学アカデミーでダゲレオタイプが公開され、同年8月19日にフランス政府が製法を「全人類への贈り物」として（イギリスを除く全世界で）無償公開した*2。この公開により技術は急速に普及したが、各ダゲレオタイプは複製不可能な一点物だった。代表作「ボールヴァール・デュ・タンプル」（c.1838）はパリの大通りを写したもので、長時間露光のため動く馬車・歩行者は写らず、靴磨きをされながら静止していた男性のみが写り込んだ——これが「写真に初めて写った人間」とされる*1。同年3月8日の研究室火災でほとんどの記録が失われ、現存確認済みの作品は25点未満に留まる*2。',
      textEn: 'Daguerre began as a theatrical designer who ran a large diorama theater in Paris. The diorama shifted painted scenes from daylight to night by changing transmitted and reflected light, and it sharpened his obsession with fixing light and image in permanent form*1. Around 1826 he began working with Nicéphore Niépce; after Niépce’s death in 1833, Daguerre kept refining a process that developed an image on a silvered plate with mercury vapor. On January 7, 1839, the daguerreotype was announced at the French Academy of Sciences, and on August 19 the French state released the process as a “gift to the world” outside Britain*2. The method spread rapidly, but each daguerreotype remained a unique, non-reproducible object. His famous view of the Boulevard du Temple (c.1838) became known for capturing what is often described as the first human figure recorded in a photograph: a man standing still long enough to have his boots polished while traffic disappeared in the long exposure*1. A studio fire on March 8, 1839 destroyed most of Daguerre’s surviving records, and fewer than twenty-five works are confirmed today*2.',
      citations: [
        { num: 1, name: 'Metropolitan Museum of Art — Daguerre and the Invention of Photography', url: 'https://www.metmuseum.org/essays/daguerre-1787-1851-and-the-invention-of-photography' },
        { num: 2, name: 'Wikipedia — Louis Daguerre', url: 'https://en.wikipedia.org/wiki/Louis_Daguerre' },
      ]
    }
  },

  {
    id: 'talbot',
    name: 'William Henry Fox Talbot',
    nameJa: 'ウィリアム・ヘンリー・フォックス・タルボット',
    nationality: 'GB',
    flag: '🇬🇧',
    years: '1800–1877',
    gender: '男性',
    era: '1839',
    movements: ['発明・技術'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/essays/william-henry-fox-talbot-british-1800-1877' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Henry_Fox_Talbot' },
      { label: 'The Met Collection', url: 'https://www.metmuseum.org/art/collection/search#!?q=fox+talbot' },
    ],
    amazon: '',
    context: {
      text: 'タルボットは1833年10月、ハネムーン中のイタリア・コモ湖でカメラ・ルシダ（光学式製図器）を用いてスケッチを試みたが、自身の画力の乏しさに深く失望した。「カメラから目を離すと、紙の上には情けない痕跡しか残っていない」と後に記している*1。この体験から「カメラが投影する像を化学的に定着できないか」という着想を得て帰国後に実験を開始。1835年の明るい夏、ラコック・アビーの敷地内に小型カメラ（妻が「ネズミ捕り」と呼んだ）を複数設置し、建物の輪郭を感光紙に記録した*2。塩化銀を染み込ませた紙ネガから複数の陽画を作るこのカロタイプ方式は後の写真文化の基盤となった。1839年1月にダゲールの成功の報せを聞き、急いで自身の発明を公表した。1844–46年刊行の写真集『自然の鉛筆』は商業出版された最初の写真入り書籍であり、写真の記録・芸術・複製としての用途を世に示した*1。ただしタルボットが特許権を厳格に管理したため、イギリスではカロタイプの普及がフランスに比べて大きく遅れた*2。',
      textEn: 'In October 1833, while on his honeymoon at Lake Como, Talbot tried to sketch with a camera lucida and was frustrated by what he saw as his own lack of drawing skill. He later wrote that once he looked away from the optical device, only a miserable trace remained on the page*1. That disappointment led him to ask whether the camera’s projected image might be fixed chemically. Back in England, he began experiments, and by the bright summer of 1835 he was placing small cameras around Lacock Abbey, using sensitized paper to record the outline of buildings*2. His calotype process, which produced multiple positive prints from a paper negative, became a foundation for photographic reproducibility. When news of Daguerre’s success arrived in January 1839, Talbot rushed to announce his own work. The Pencil of Nature, published in parts between 1844 and 1846, became the first commercially published book illustrated with photographs and demonstrated photography as record, art, and reproducible medium*1. Yet Talbot’s strict patent control also slowed the spread of the calotype in Britain compared with France*2.',
      citations: [
        { num: 1, name: 'Metropolitan Museum of Art — William Henry Fox Talbot', url: 'https://www.metmuseum.org/essays/william-henry-fox-talbot-1800-1877-and-the-invention-of-photography' },
        { num: 2, name: 'V&A — William Henry Fox Talbot', url: 'https://www.vam.ac.uk/articles/william-henry-fox-talbot-an-introduction' },
      ]
    }
  },

  {
    id: 'fenton',
    name: 'Roger Fenton',
    nameJa: 'ロジャー・フェントン',
    nationality: 'GB',
    flag: '🇬🇧',
    years: '1819–1869',
    gender: '男性',
    era: '1839',
    movements: ['ドキュメンタリー', '戦争写真'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/artists/1898' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Roger_Fenton' },
      { label: 'The Met Collection', url: 'https://www.metmuseum.org/art/collection/search?q=roger+fenton' },
    ],
    amazon: '',
    context: {
      text: 'フェントンは1853年に英国王立写真協会（ロイヤル・フォトグラフィック・ソサエティ）の設立に中心的役割を果たした弁護士出身の写真家だった*1。1854年のクリミア戦争で従軍記者ウィリアム・ハワード・ラッセル（タイムズ紙）が英国軍の失態を連報したことで、戦争は国内で深刻に不人気となった。マンチェスターの出版業者トーマス・アグニュー商会はプリンス・アルバートを通じて政府の協力を取り付け、「否定的な世論を和らげる写真」を撮るためフェントンを現地に派遣した*2。アグニューは「死体・残虐な場面は撮影しないこと」を明示的に要請しており、フェントンの360点の写真には死傷者・戦闘の場面がほぼ存在しない*1。代表作「死の影の谷」（砲弾が散乱する道）については、ジャーナリストのエロール・モリスが後に二種類の写真の比較から「砲弾を並べ替えて演出した可能性がある」と論証し、写真の「真実性」を問う議論を呼んだ*2。フェントンは1862年に突然写真活動を終え、機材を売却して法律家に戻った。',
      textEn: 'Fenton, trained as a lawyer, became one of the key figures behind the founding of the Royal Photographic Society in 1853*1. During the Crimean War, William Howard Russell’s dispatches for The Times exposed the failures of the British army and made the war deeply unpopular at home. The Manchester publisher Thomas Agnew & Sons, working with support routed through Prince Albert, arranged for Fenton to travel to the front and produce photographs that might soften negative public opinion*2. Agnew explicitly instructed him not to photograph corpses or scenes of extreme violence, so among Fenton’s roughly 360 images, almost none show direct combat or the dead*1. His best-known picture, The Valley of the Shadow of Death, later became central to debates about photographic truth when Errol Morris argued that the cannonballs visible in the scene may have been rearranged for effect*2. Fenton abruptly left photography in 1862, sold his equipment, and returned to legal work.',
      citations: [
        { num: 1, name: 'Library of Congress — Fenton Crimean War Photographs', url: 'https://www.loc.gov/collections/fenton-crimean-war-photographs/about-this-collection/' },
        { num: 2, name: 'Metropolitan Museum of Art — Roger Fenton', url: 'https://www.metmuseum.org/essays/roger-fenton-1819-1869' },
      ]
    }
  },

  {
    id: 'beato',
    name: 'Felice Beato',
    nameJa: 'フェリーチェ・ベアト',
    nationality: 'IT / GB',
    flag: '🇮🇹',
    years: '1832–1909',
    gender: '男性',
    era: '1839',
    movements: ['ドキュメンタリー', '戦争写真', '植民地写真'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/art/collection/search?q=felice+beato' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Felice_Beato' },
    ],
    amazon: '',
    context: {
      text: 'ヴェネツィア生まれでイギリスに帰化したベアトは、1855年のクリミア戦争取材を皮切りに英仏軍が展開する場所へと同行し続けた写真家だった*1。1857–58年のインド大反乱後のラクナウでは、骸骨が散乱するセカンダーラバーグの「事後の現場」を撮影した（数ヶ月後の再訪撮影であり、遺体配置の演出が指摘されることもある）。1860年の第二次アヘン戦争では英仏連合軍に従い中国各地を撮影した。その際に知り合った英国人挿絵記者チャールズ・ウィルグマンとともに1863年に横浜へ移り、「ベアト＆ウィルグマン」スタジオを開設した*2。ベアトは「西洋人が東洋の何を求めているか」を正確に把握しており、日本の風景・人物・風俗を外国人旅行者向けに写真帖として販売した。日本では写真の手彩色技法を広め、幕末から明治初期の日本社会を記録した*1。彼の視線は帝国主義の文脈に置かれており、今日の研究者はその権力関係を批判的に検討している*2。',
      citations: [
        { num: 1, name: 'Wikipedia — Felice Beato', url: 'https://en.wikipedia.org/wiki/Felice_Beato' },
        { num: 2, name: "MIT Visualizing Cultures — Beato's Japan", url: 'https://visualizingcultures.mit.edu/beato_places/essay.pdf' },
      ]
    }
  },

  {
    id: 'nadar',
    name: 'Nadar',
    nameJa: 'ナダール',
    nationality: 'FR',
    flag: '🇫🇷',
    years: '1820–1910',
    gender: '男性',
    era: '1839',
    movements: ['ポートレート'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/art/collection/search?q=nadar' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Nadar_(photographer)' },
    ],
    amazon: '',
    context: {
      text: 'ナダール（本名ガスパール＝フェリックス・トゥルナション）はジャーナリスト・風刺漫画家として当代の文化人と深く交流していたが、1853年頃から写真家に転身した*1。人物の内面を見抜く取材者としての眼が、肖像写真家としての強みとなった。当時主流だった刺繍背景・小道具・仰々しい衣装を排し、グレーの無地背景と自然光のみで撮影したのは「余計な装飾が被写体の個性を隠してしまう」という判断からだった。ヴィクトル・ユゴー・サラ・ベルナール・シャルル・ボードレール・エクトル・ベルリオーズらのポートレートでその方法論を示した*2。1858年には気球から世界初の航空写真を撮影し、1861年にはパリの地下道（カタコンブ・下水道）でアーク灯を用いた初の電灯撮影を行った。写真撮影の技術的可能性を拡張しながら、1874年には自身のスタジオを印象派の画家たちに無償で提供し第1回印象派展の会場となった——写真の普及が肖像画市場を変え、印象派の登場を後押しした時代の交差点にナダールは立っていた*1。',
      citations: [
        { num: 1, name: 'Britannica — Nadar', url: 'https://www.britannica.com/biography/Nadar' },
        { num: 2, name: 'Wikipedia — Nadar', url: 'https://en.wikipedia.org/wiki/Nadar_(photographer)' },
      ]
    }
  },

  {
    id: 'legray',
    name: 'Gustave Le Gray',
    nameJa: 'ギュスターヴ・ル・グレー',
    nationality: 'FR',
    flag: '🇫🇷',
    years: '1820–1884',
    gender: '男性',
    era: '1839',
    movements: ['風景写真', '発明・技術'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/art/collection/search?q=gustave+le+gray' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Gustave_Le_Gray' },
    ],
    amazon: '',
    context: {
      text: 'パリで絵画を学んだル・グレーは1840年代後半から写真家に転身し、ナダールらを育てた写真学校をパリに開いた*1。代表作の海景写真は技術的な難題から生まれた。ガラス湿板（コロジオン法）は水面と空では必要露光時間が大きく異なり、一枚のネガで両者を適切に写すことができなかった——空に合わせれば海面は暗くなり、海面に合わせれば空は白くとびる。ル・グレーの解決策は、海と空で別々に露光した2枚のネガを暗室で合成する「コンビネーション・プリント」だった。当時この手法を一切公言しなかったため、批評家は両者が同時に写り込んだ光景に驚嘆した*2。1857年の「大波」はその技術の頂点を示す作品とされる。1851年頃に開発した「ワックス紙ネガ法」もカロタイプの改良として現地準備時間を短縮した。1860年頃に財政難でフランスを去り、エジプト・カイロに移住。スタジオを開いて写真家・デッサン教師として働き、1884年にカイロで没した。パリでの活躍に比べ晩年は忘れられた存在となったが、20世紀後半以降に再評価が進んでいる*1。',
      citations: [
        { num: 1, name: 'Wikipedia — Gustave Le Gray', url: 'https://en.wikipedia.org/wiki/Gustave_Le_Gray' },
        { num: 2, name: "Nonsite.org — Photography and the Philosophy of Time: On Gustave Le Gray's Great Wave", url: 'https://nonsite.org/photography-and-the-philosophy-of-time/' },
      ]
    }
  },

  /* ────────── 1870–1890s ────────── */
  {
    id: 'muybridge',
    name: 'Eadweard Muybridge',
    nameJa: 'エドワード・マイブリッジ',
    nationality: 'GB / US',
    flag: '🇬🇧',
    years: '1830–1904',
    gender: '男性',
    era: '1870',
    movements: ['科学写真', '実験的技法'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Eadweard_Muybridge' },
      { label: 'Kingston Museum', url: 'https://www.kingstonmuseum.co.uk/eadweard-muybridge/' },
      { label: 'Wikimedia Commons', url: 'https://commons.wikimedia.org/wiki/Eadweard_Muybridge' },
    ],
    amazon: '',
    context: {
      text: 'スタンフォード大学創設者でもあるリーランド・スタンフォードは、馬が疾走中に四肢をすべて地面から離す瞬間があるかどうかという当時未解決の科学論争に写真で決着をつけるため、1872年頃にマイブリッジに撮影を依頼した*1。当初の実験は技術的限界から不明瞭だったが、マイブリッジはシャッター機構を改良し続け、1878年6月にパロ・アルトのスタンフォード牧場でコース沿いに24台のカメラを設置して馬が順次トリップワイヤーを踏む方式の連続撮影に成功した。「馬の動き」は四肢が同時に地面を離れる瞬間を視覚的に証明し、即座に世界の新聞に転載された*2。マイブリッジはこの成果をさらに「動かして見せる」ために、1879年に連続写真をガラス円盤に描いてスクリーンに投影する「ズープラキシスコープ」を発明した——映画の前身とされる装置であり、1888年にエジソンがマイブリッジと面会してキネトスコープ（映写機）開発に着手する契機となった*1。1883–86年にはフィラデルフィア大学の支援を受けて人体・動物の多様な動作を体系的に撮影し、11巻の写真集『動物の動作』（1887年）として刊行した。1893年のシカゴ万博では「ズープラキシグラフィカル・ホール」でプロジェクション上映を行い、スタンフォードとはその後写真集の著作権をめぐる訴訟に発展した*2。',
      citations: [
        { num: 1, name: 'Wikipedia — Eadweard Muybridge', url: 'https://en.wikipedia.org/wiki/Eadweard_Muybridge' },
        { num: 2, name: 'Britannica — Eadweard Muybridge', url: 'https://www.britannica.com/biography/Eadweard-Muybridge' },
      ]
    }
  },

  {
    id: 'marey',
    name: 'Étienne-Jules Marey',
    nameJa: 'エティエンヌ＝ジュール・マレー',
    nationality: 'FR',
    flag: '🇫🇷',
    years: '1830–1904',
    gender: '男性',
    era: '1870',
    movements: ['科学写真', '実験的技法'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/%C3%89tienne-Jules_Marey' },
      { label: 'Musée Marey', url: 'https://musee-marey.fr' },
    ],
    amazon: '',
    context: {
      text: 'コレージュ・ド・フランスで生理学を研究していたマレーは、心臓・筋肉・神経の運動を計測する研究を進める中で、「肉眼では観察できない速い動作をどう記録するか」という問題に直面していた。1878年頃にマイブリッジの連続写真に接したことで、写真を科学的計測の道具として採用することを決意した*1。ただしマイブリッジが複数のカメラで各瞬間を別々に記録したのに対し、マレーは「運動の軌跡全体を一枚の乾板に収める」ことで動作の連続的な変化を可視化することを目指し、1882年に回転式ガラス板カメラ「クロノフォトグラフィック・ガン」を発明した。毎秒12コマで撮影し、鳥の飛翔・人体の歩行・落下する猫などを一画面に多重露光した*2。「時系列の動きを空間として表現する」このアプローチは、1910年代にイタリア未来派（フュトゥリスモ）の画家ジャコモ・バッラらが絵画における動体表現の視覚的参照源とし、マルセル・デュシャンの「階段を降りる裸体No.2」（1912年）にも影響を与えたとされる。フランス政府の支援のもとで行った研究は医学・体育・軍事訓練の分野にも応用され、リュミエール兄弟の映画開発の直接的な前史をなすと位置づけられている*1。',
      citations: [
        { num: 1, name: 'Wikipedia — Étienne-Jules Marey', url: 'https://en.wikipedia.org/wiki/%C3%89tienne-Jules_Marey' },
        { num: 2, name: 'Britannica — Étienne-Jules Marey', url: 'https://www.britannica.com/biography/Etienne-Jules-Marey' },
      ]
    }
  },

  {
    id: 'riis',
    name: 'Jacob Riis',
    nameJa: 'ジェイコブ・リース',
    nationality: 'DK / US',
    flag: '🇩🇰',
    years: '1849–1914',
    gender: '男性',
    era: '1870',
    movements: ['社会ドキュメンタリー', 'ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Jacob_Riis' },
      { label: 'MoMA', url: 'https://www.moma.org/artists/4978' },
      { label: 'Library of Congress', url: 'https://www.loc.gov/pictures/collection/ggbain/item/ggb2005025700/' },
    ],
    amazon: '',
    context: {
      text: 'デンマーク出身のリースは1870年にアメリカへ移民し、自身も極貧・失業・路上生活を経験した後に記者へと転じた*1。ニューヨーク・イブニング・サンの警察担当記者としてロウアーイーストサイドのテネメント（過密集合住宅）の実態を目撃し、「言葉では伝わらない現実を見せる方法」として1887年頃からマグネシウム・フラッシュを使った室内撮影を試みた——当時の感光材料では暗い屋内を照らすにはフラッシュ以外に手段がなかった*2。突然の閃光で驚かせながら撮影する方法は今日批判的に検討されているが、1890年刊行の『向こう半分の人々はどう暮らしているか』は中産階級の読者に移民貧困層の住環境を初めて視覚的に示した。セオドア・ルーズベルト（当時ニューヨーク警察委員長）は本書に感銘を受け、翌朝リース宅を訪問して「あなたの仕事をしたい、何でも協力する」とメモを残したと伝わる*1。この出会いがテネメント住宅改革法の成立につながった。写真を社会変革の手段として意図的に使った初期の先例として位置づけられる一方、アイルランド系・ユダヤ系・中国系移民への固定観念を反映する視点は現代の研究者によって批判的に再評価されている*2。',
      citations: [
        { num: 1, name: 'Wikipedia — Jacob Riis', url: 'https://en.wikipedia.org/wiki/Jacob_Riis' },
        { num: 2, name: 'Smithsonian Magazine — Jacob Riis', url: 'https://www.smithsonianmag.com/history/how-jacob-riis-exposed-shame-new-york-city-slums-180956836/' },
      ]
    }
  },

  {
    id: 'marville',
    name: 'Charles Marville',
    nameJa: 'シャルル・マルヴィル',
    nationality: 'FR',
    flag: '🇫🇷',
    years: '1813–1879',
    gender: '男性',
    era: '1870',
    movements: ['ドキュメンタリー', '都市記録'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/art/collection/search?q=charles+marville' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Charles_Marville' },
      { label: 'Bibliothèque Historique de la Ville de Paris', url: 'https://bibliotheques-specialisees.paris.fr' },
    ],
    amazon: '',
    context: {
      text: 'マルヴィルは19世紀前半から挿絵画家・銅版画家として活動していたが、写真技術の登場後に転身した*1。1853年にナポレオン3世の命を受けたジョルジュ＝ウジェーヌ・オスマン男爵がパリの大規模近代化改造を開始すると、マルヴィルはパリ市公式写真家として取り壊し前の街区を記録するよう行政から命じられた——改造の正当性を示す「ビフォー・アフター」記録として依頼されたものだった*2。オスマン改造は中世来の路地・密集街区を広大なブールヴァール・下水道・公園に置き換えることで衛生・交通・治安の改善を目指したが、同時に中世以来の都市の記憶を消し去るものでもあった。マルヴィルは取り壊し直前のノートルダム大聖堂周辺・シテ島・レ・アル地区などを湿板コロジオン法の大判カメラで体系的に撮影し、約900点が現在パリ市立歴史図書館（BHVP）に収蔵されている*1。「改善のための行政記録」として依頼された写真が、結果として近代化が消し去った都市の記憶の集成となった——この「公的委嘱が批評的アーカイブを生み出す」逆説は、その後のドキュメンタリー写真史に繰り返し現れるパターンとして参照されている*2。',
      citations: [
        { num: 1, name: 'Wikipedia — Charles Marville', url: 'https://en.wikipedia.org/wiki/Charles_Marville' },
        { num: 2, name: 'Metropolitan Museum of Art — Charles Marville', url: 'https://www.metmuseum.org/art/collection/search?q=charles+marville' },
      ]
    }
  },

  {
    id: 'annan',
    name: 'Thomas Annan',
    nameJa: 'トーマス・アナン',
    nationality: 'GB',
    flag: '🇬🇧',
    years: '1829–1887',
    gender: '男性',
    era: '1870',
    movements: ['社会ドキュメンタリー', 'ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Thomas_Annan_(photographer)' },
      { label: 'Glasgow Museums', url: 'https://www.glasgowmuseums.com' },
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/art/collection/search?q=thomas+annan' },
    ],
    amazon: '',
    context: {
      text: 'グラスゴーでは19世紀中頃からコレラ・腸チフスが繰り返し流行し、当局はその温床を旧市街の密集路地「クローズ」に求めた。1866年の市条例に基づき設立されたグラスゴー市改善委員会は旧街区の撤去・再開発を決定し、記録写真を行政の文書化手段として採用した*1。その委嘱を受けたアナンは1868–71年に湿板コロジオン法で路地を撮影し、後に乾板法で再撮影・拡充した1877–79年版（計71点）を「グラスゴーの古い路地と街路の写真」として刊行した。仄暗い路地に佇む住民・洗濯物・石畳を正面から捉えた写真は、撤去の正当性を示すための記録として依頼されたものだったが、結果としてグラスゴー労働者階級の生活環境の証言となった*2。リース（ニューヨーク、1888–90年）より20年早く公的委嘱による都市貧困環境の記録という先例を作り、「改善のための記録が貧困の証言になる」という写真の逆説的機能を初期に示した事例とされる。アナンの息子ジェームズ・クレイグ・アナンはウィーン分離派とも交流したピクトリアリズムの写真家として活躍した*1。',
      citations: [
        { num: 1, name: 'Wikipedia — Thomas Annan', url: 'https://en.wikipedia.org/wiki/Thomas_Annan_(photographer)' },
        { num: 2, name: 'Metropolitan Museum of Art — Thomas Annan', url: 'https://www.metmuseum.org/art/collection/search?q=thomas+annan' },
      ]
    }
  },

  /* ────────── 1839–1860s（再掲） ────────── */
  {
    id: 'brady',
    name: 'Mathew Brady',
    nameJa: 'マシュー・ブレイディ',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1822–1896',
    gender: '男性',
    era: '1839',
    movements: ['ポートレート', 'ドキュメンタリー', '戦争写真'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Mathew_Brady' },
      { label: 'Wikimedia Commons', url: 'https://commons.wikimedia.org/wiki/Mathew_Brady' },
      { label: 'Library of Congress', url: 'https://www.loc.gov/pictures/collection/cwp/brady.html' },
    ],
    amazon: '',
    context: {
      text: 'ニューヨーク出身のブレイディは1840年代から大統領を含む著名人の肖像写真で名声を築き、アメリカ最高の肖像写真家と呼ばれた*1。1861年の南北戦争勃発にあたり「戦争は写真で記録されなければならない」という確信から私財を投じて20人以上の写真家チームを組織し、携帯暗室馬車で各戦場に派遣した。彼自身は晩年に「ある精神が私の足に《行け》と言い、私は行った」と語っている*2。アレクサンダー・ガードナー、ティモシー・オサリヴァンら傘下の写真家が残した記録は1万枚以上に上る。1862年10月、ガードナーが撮影したアンティータムの戦場死者の写真がブレイディのニューヨーク・ギャラリーで展示された——アメリカ市民が戦場の死者の写真を目にした最初の機会であり、ニューヨーク・タイムズは「ブレイディ氏は戦争の恐ろしい現実を我々の目の前に持ち込んだ」と報じた*1。戦後、政府はネガの買取を拒否し、ブレイディは破産。1875年に議会が2万5千ドルで購入したが（自身が投じた費用の4分の1以下）、彼は極貧のまま1896年に没した*2。',
      citations: [
        { num: 1, name: 'Wikipedia — Mathew Brady', url: 'https://en.wikipedia.org/wiki/Mathew_Brady' },
        { num: 2, name: 'Library of Congress — Brady-Handy Photograph Collection', url: 'https://www.loc.gov/pictures/collection/cwp/brady.html' },
      ]
    }
  },

  {
    id: 'cameron',
    name: 'Julia Margaret Cameron',
    nameJa: 'ジュリア・マーガレット・キャメロン',
    nationality: 'GB',
    flag: '🇬🇧',
    years: '1815–1879',
    gender: '女性',
    era: '1839',
    movements: ['ピクトリアリズム', 'ポートレート'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/artists/992' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Julia_Margaret_Cameron' },
      { label: 'The Met Collection', url: 'https://www.metmuseum.org/art/collection/search?q=julia+margaret+cameron' },
      { label: 'Victoria & Albert Museum', url: 'https://www.vam.ac.uk/collections/photography?q=julia+margaret+cameron' },
    ],
    amazon: '',
    context: {
      text: 'キャメロンは1815年にカルカッタで生まれ、詩人テニスン・科学者ハーシェルらと親交を持つヴィクトリア朝のインテリゲンチャの中にいた。1863年、娘からカメラを贈られた時、彼女は48歳だった*1。ハーシェル卿への手紙でキャメロンは「私の志は写真を高貴にし、それに高い芸術の性格と用途を与えることだ」と記している——この言葉が彼女の写真活動全体の目的を示す*2。その手段として当時の標準（鮮鋭な像）を意図的に外したソフトフォーカスを選んだ。長時間露光・浅い被写界深度・低照明を組み合わせ、化学薬品の染みや指紋もそのまま残した。「技術的欠陥」と批判されたが、キャメロンは「写真の真実は精密さではなく内面を喚起することにある」と信じた*1。チャールズ・ダーウィン・テニスン・カーライルらのポートレート、アーサー王伝説・聖書をテーマにした構成作品を残した。作品は大判（約38×30cm）で制作され、絵画と比較できる規模を持っていた。1875年にセイロン（現スリランカ）へ移住し、1879年に没した*2。',
      citations: [
        { num: 1, name: "V&A — Julia Margaret Cameron's working methods", url: 'https://www.vam.ac.uk/articles/julia-margaret-camerons-working-methods' },
        { num: 2, name: 'Wikipedia — Julia Margaret Cameron', url: 'https://en.wikipedia.org/wiki/Julia_Margaret_Cameron' },
      ]
    }
  },

  /* ────────── 1890–1910s ────────── */
  {
    id: 'emerson',
    name: 'Peter Henry Emerson',
    nameJa: 'ピーター・ヘンリー・エマーソン',
    nationality: 'GB',
    flag: '🇬🇧',
    years: '1856–1936',
    gender: '男性',
    era: '1890',
    movements: ['自然主義写真', 'ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Peter_Henry_Emerson' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/Peter-Henry-Emerson' },
      { label: 'Tate Papers — Emerson\'s Evolution', url: 'https://www.tate.org.uk/research/tate-papers/27/emersons-evolution' },
    ],
    amazon: '',
    context: {
      text: 'エマーソンがスタジオ演出を「不正直」と批判し、単一ネガ・単一露光による写真を芸術の条件とした根拠は、ドイツの生理学者ヘルマン・フォン・ヘルムホルツの視覚生理学にあった。ヘルムホルツは網膜中心窩のみが鮮明に見え、周辺視野は自動的に軟化するという人間の視覚特性を解明しており、エマーソンは1889年の著書『芸術学生のための自然主義写真論』でこの理論を写真に適用した*1。主要被写体のみを鮮明に、周辺はやや軟焦点にする「差動焦点法」こそが人間の視覚に最も忠実であり、それゆえ芸術的表現として価値を持つという論理だった。哲学的基盤はハーバート・スペンサーの進化心理学——「心は外部刺激を受動的に受け取る」という立場——であり、カメラの光学プロセスが人間知覚を科学的に再現できると主張した*2。複数ネガを合成するコンビネーションプリントやスタジオの人工的配置は、この自然な視覚体験を歪める「不正直」な操作とみなした。代表作は東アングリアの漁師・農民の生活を記録した写真集『ノーフォーク・ブローズの生活と風景』（1886年）であり、写真集という形式で芸術的意図を示す試みでもあった*3。しかし1891年、ハーター＆ドリフィールドの研究が露光の機械的法則を証明し、ウィリアム・ジェームズが「心は外部刺激に能動的に関与する」と反証したことで哲学的基盤が崩れ、エマーソンは「自然主義写真の死」と題した黒縁のパンフレットを写真界に送り自説を撤回した*4。撤回はエマーソンが写真の芸術性の主張を諦めたことを意味したが、「写真が絵画を模倣せず、写真固有の視覚原理を根拠に芸術性を論証しようとした最初の試み」として、後のストランドやウェストンらのストレート写真理論の先駆けとなった*5。また若きアルフレッド・スティーグリッツを見出し励ましを与えた事実も記録されており、20世紀写真史の中心へとつながる橋渡しの役割を果たした*1。',
      citations: [
        { num: 1, name: 'Tate Papers — Emerson&#39;s Evolution', url: 'https://www.tate.org.uk/research/tate-papers/27/emersons-evolution' },
        { num: 2, name: 'Art History Unstuffed — Peter Henry Emerson (1856–1936)', url: 'https://arthistoryunstuffed.com/peter-henry-emerson-1856-1936/' },
        { num: 3, name: 'Minneapolis Institute of Art — Peter Henry Emerson and American Naturalistic Photography', url: 'https://new.artsmia.org/press/peter-henry-emerson-and-american-naturalistic-photography' },
        { num: 4, name: 'Internet Archive — The Death of Naturalistic Photography [1890]', url: 'https://archive.org/details/1890Death_naturalistic_photography-BP21-6' },
        { num: 5, name: 'On Landscape — Peter Henry Emerson', url: 'https://www.onlandscape.co.uk/2020/09/peter-henry-emerson/' },
      ]
    }
  },

  {
    id: 'stieglitz',
    name: 'Alfred Stieglitz',
    nameJa: 'アルフレッド・スティーグリッツ',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1864–1946',
    gender: '男性',
    era: '1890',
    movements: ['ピクトリアリズム', '写真分離派', 'ストレート写真'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/essays/alfred-stieglitz-1864-1946-and-american-photography' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Alfred_Stieglitz' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/Alfred-Stieglitz' },
      { label: 'V&A', url: 'https://www.vam.ac.uk/articles/alfred-stieglitz-pioneer-of-modern-photography' },
    ],
    amazon: '',
    context: {
      text: '1890年代のニューヨークでは写真は「機械的な複写装置」とみなされ、絵画・彫刻と同列の芸術として美術館に展示される対象ではなかった。スティーグリッツが写真の芸術的地位を高めようとしたのは、この文化的偏見と正面から戦うためだった*1。初期のピクトリアリズムの段階では——軟焦点・ゴム重クロム酸塩プリント・絵画的構図——を駆使して「写真も絵画に匹敵する」ことを示そうとした。1902年に結成した写真分離派の目的をスティーグリッツ自身は「ピクトリアル写真に傾倒したアメリカ人たちをまとめ、それが個人的表現の独自媒体として認められるよう努める」と定義した*2。1903年創刊の写真誌『カメラ・ワーク』と1905年開廊のギャラリー291は、写真を絵画と同じ文脈に置く制度的戦略だった。291ではマティス（1908年）・セザンヌ・ピカソ（1911年）らのアメリカ初個展を開催し、前衛絵画と並置することで「写真は芸術か」という問い自体を時代遅れにしようとした*3。しかし第一次世界大戦後、スティーグリッツはピクトリアリズムの方針——絵画を模倣することで芸術性を証明する——が根本的に誤りだと気づいた。モダニズムの核心は「素材固有の特性を尊重する」ことにあり、写真が絵画を真似することはその独自性を自ら否定することだったのである*4。「ストレート写真」への転換後、1922年から始めた「エクイヴァレンツ」では雲の連作約350点を制作し、「写真は被写体によらず内的状態の等価物たりうる」と宣言した——写真が純粋に抽象的な感情の記録になりうることを初めて主張した作品群である*5。批評家ヒルトン・クレイマーはエクイヴァレンツが「1940〜50年代のアメリカ絵画に現れるまで到達しなかった種類の抒情的抽象に達していた」と評した*6。',
      citations: [
        { num: 1, name: 'Metropolitan Museum of Art — Alfred Stieglitz (1864–1946) and American Photography', url: 'https://www.metmuseum.org/essays/alfred-stieglitz-1864-1946-and-american-photography' },
        { num: 2, name: 'The Art Story — Alfred Stieglitz', url: 'https://www.theartstory.org/artist/stieglitz-alfred/' },
        { num: 3, name: 'V&A — Alfred Stieglitz: Pioneer of Modern Photography', url: 'https://www.vam.ac.uk/articles/alfred-stieglitz-pioneer-of-modern-photography' },
        { num: 4, name: 'Aesthetics of Photography — Alfred Stieglitz', url: 'https://aestheticsofphotography.com/alfred-stieglitz/' },
        { num: 5, name: 'Art Institute of Chicago — Alfred Stieglitz Collection: Equivalents', url: 'https://archive.artic.edu/stieglitz/equivalents/' },
        { num: 6, name: 'Modernism/Modernity Print+ — Unrarified Air: Stieglitz and the Modernism of Equivalence', url: 'https://modernismmodernity.org/articles/unrarified-air' },
      ]
    }
  },

  {
    id: 'kasebier',
    name: 'Gertrude Käsebier',
    nameJa: 'ガートルード・ケーゼビア',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1852–1934',
    gender: '女性',
    era: '1890',
    movements: ['ピクトリアリズム', '写真分離派', 'ポートレート'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/calendar/exhibitions/365' },
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/art/collection/search/267530' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Gertrude_K%C3%A4sebier' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/Gertrude-Kasebier' },
    ],
    amazon: '',
    context: {
      text: 'ケーゼビアが「人物写真とは伝記であれ——被写体の本質的な気質・魂・人間性を一枚の写真に引き出す」を信念としたのは、当時のニューヨーク商業写真スタジオが「技術的正確さ」の競争に終始していたからである*1。19世紀末の肖像写真は照明・ポーズを規格化した名刺判写真の延長であり、被写体の内面は記録の対象外だった。ケーゼビアはプラット・インスティチュートで絵画を学んだ経験から、「一枚の絵で何を省くかの識別眼こそが構図と感情を決定する」と考えており、この原則を肖像写真に持ち込んだ*2。彼女は撮影前に被写体と長時間を過ごし、「演出されていても真正に見える」効果を追求した。代表作「女たちの中に祝福された人よ」（1899年）では、詩人アグネス・リーと娘ペギーを二部屋の境の敷居に立たせ、壁の「受胎告知」版画と呼応させることで母から娘への世代の継承を聖書的文脈に置いた*3。プラチナプリントとゴム重クロム酸塩の操作によって、ガラス板ネガが持つ鮮鋭な細部を意図的に軟化させ、「絵画としての写真」を実現した*4。ケーゼビアが商業スタジオを経営しながら芸術的実践を貫いたのは、彼女自身の経済的自立への必要性でもあった。夫との不幸な結婚のなかで三人の子を育て、37歳でプラットに入学し、1897年にフィフス・アベニューに独立スタジオを開設した。スティーグリッツは彼女を「この国の肖像写真家として疑いなくリーダー」と評した*5。後の写真批評では、彼女の制作したジェンダー化されたイメージ——母性・聖性・「ヨーク（멍에）」をテーマとする作品——と私生活の乖離が、フェミニズムの視点から論じられている*6。',
      citations: [
        { num: 1, name: 'All About Photo — Gertrude Käsebier', url: 'https://www.all-about-photo.com/photographers/photographer/1632/gertrude-kasebier' },
        { num: 2, name: 'The Portrait Photography of Gertrude Käsebier — Different Drum', url: 'http://litflower.com/portrait-photography-gertrude-kasebier/' },
        { num: 3, name: 'Brooklyn Museum — Blessed Art Thou Among Women', url: 'https://brooklynmuseum.org/objects/111126' },
        { num: 4, name: 'Delaware Art Museum — Women in Pictorialist Photography: Gertrude Käsebier', url: 'https://exhibitions.lib.udel.edu/women-in-pictorialist-photography/gertrude-kasebier%EF%BF%BC/' },
        { num: 5, name: 'Art Institute of Chicago — Gertrude Käsebier (Alfred Stieglitz Collection)', url: 'https://archive.artic.edu/stieglitz/gertrude-kaesebier/' },
        { num: 6, name: 'Artsy — Gertrude Käsebier&#39;s Camera-Box Heart', url: 'https://www.artsy.net/article/machamux-photographer-gertrude-kasebier-camera-box-heart' },
      ]
    }
  },

  {
    id: 'steichen',
    name: 'Edward Steichen',
    nameJa: 'エドワード・スタイケン',
    nationality: 'LU / US',
    flag: '🇱🇺',
    years: '1879–1973',
    gender: '男性',
    era: '1890',
    movements: ['ピクトリアリズム', '写真分離派', 'ポートレート'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/essays/edward-j-steichen-1879-1973-the-photo-secession-years' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Edward_Steichen' },
      { label: 'The Art Story', url: 'https://www.theartstory.org/artist/steichen-edward/' },
    ],
    amazon: '',
    context: {
      text: 'スタイケンがピクトリアリズムに向かった出発点は、写真が絵画と同等の芸術的地位を得るためには「絵画のように見える」ことが最も有効な戦略だという判断だった。ルクセンブルク生まれでアメリカ育ちのスタイケンは幼少期から絵を描き、ジェームズ・ホイッスラーのトーナリズム——霧と光の微妙な階調が感情を喚起する絵画——を深く吸収していた*1。プラチナ・ゴム重クロム酸塩多層刷りで同一ネガから3種の色調を生み出した「フラットアイアン」（1904年）は、「印刷プロセスそのものを絵画制作の場」として使う方法論を体現しており、「写真が絵画に規模・色彩・個性・表現において拮抗できる」ことの実証だった*2。1907年には「薄暮の3枚のプラチナプリント」が1000ドルで売れ——当時の写真作品として異例の高値——、ピクトリアリズムが芸術市場に受け入れられた証となった*1。しかし第一次世界大戦が転換点となった。陸軍写真部門の指揮官として航空偵察写真を統括したスタイケンは、精密・直接・操作なしの記録こそが写真固有の能力であることを経験的に確信した*3。戦後スタイケンは「私は画家として高級な壁紙に金枠をつけていたに過ぎなかった——全部燃やした」と語り絵画を捨て、コンデ・ナスト社の「ヴォーグ」「ヴァニティ・フェア」の首席写真家として人工照明・高コントラスト・鮮鋭焦点のストレート写真に転換した*4。1947年にMoMAの写真部門ディレクターに就任し、1955年の「人間家族」展を企画した——68カ国503名・503点の写真で「人類の共通性」を訴えた展覧会は38カ国を巡回し900万人が鑑賞した。写真が美術館制度の中で大衆と共有される媒体として確立した出来事だった*5。',
      citations: [
        { num: 1, name: 'Metropolitan Museum of Art — Edward J. Steichen: The Photo-Secession Years', url: 'https://www.metmuseum.org/essays/edward-j-steichen-1879-1973-the-photo-secession-years' },
        { num: 2, name: 'Metropolitan Museum of Art — The Flatiron (collection)', url: 'https://www.metmuseum.org/art/collection/search/267803' },
        { num: 3, name: 'The Art Story — Edward Steichen', url: 'https://www.theartstory.org/artist/steichen-edward/' },
        { num: 4, name: 'Family of Man Education — Edward Steichen: From a man of his time to an artist out of time', url: 'https://www.thefamilyofman.education/en/historical-context/edward-steichen-from-a-man-of-his-time-to-an-artist-out-of-time' },
        { num: 5, name: 'ICP — Edward Steichen', url: 'https://www.icp.org/browse/archive/constituents/edward-steichen' },
      ]
    }
  },

  {
    id: 'demachy',
    name: 'Robert Demachy',
    nameJa: 'ロベール・ドマシー',
    nationality: 'FR',
    flag: '🇫🇷',
    years: '1859–1936',
    gender: '男性',
    era: '1890',
    movements: ['ピクトリアリズム'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/art/collection/search/289550' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Robert_Demachy' },
      { label: 'Monovisions — Robert Demachy Biography', url: 'https://monovisions.com/robert-demachy-biography-pictorial-photographer/' },
    ],
    amazon: '',
    context: {
      text: 'ドマシーの芸術写真論の核心は「自然はしばしば美しいが、そのままでは決して芸術的ではない。芸術作品には芸術家の介入が不可欠であり、ストレート写真はテーマを記録するだけだ」という立場にあった*1。この主張の下敷きにあるのは、19世紀フランス美術における「自然のコピーではなく転写」という芸術観——エドガー・ドガが踊り子を光と運動の印象として描いたように、芸術家は目の前の光景をそのまま複写するのではなく、感覚の等価物を構成すべきだという考えだった*2。ドマシーはこの理念の実践手段として、ゴム重クロム酸塩プリントを選んだ。感光した顔料ゴム液を水で洗い流す工程で、アーティストが針やブラシで像を直接操作できる技法である。ドマシーはこれを「写真アクアチント」と命名し、銅版画と同列の版画芸術として写真を位置づけようとした——版画家が金属板に手を加えて唯一の印刷物を作るように、写真家も印刷段階で介入することで芸術的価値を生み出せるという論理だった*3。代表作「速度」（1904年）はダンサーの像を印刷段階で激しく引き伸ばし・ぼかして動感を表現した作品で、「カメラが捉えた瞬間」ではなく「アーティストが構成した運動の観念」を提示するものである*4。1895年にパリ・ロンドン・ブリュッセルで初のガム印画を発表した際、「写真革命」と評された——この文脈でスティーグリッツは1904年にドマシーを「ガム印刷の父」と称し『カメラ・ワーク』で積極的に紹介した*5。ドマシーは生涯に1000点以上の写真評論を執筆し操作写真を理論的に擁護し続けたが、1914年に突然写真を止め素描に転じた。その理由は現在も文献上説明されていない*6。',
      citations: [
        { num: 1, name: 'New Old Photography — Robert Demachy, French 1859–1936', url: 'https://platinumprince.com/individual-pictorialists/2019/4/3/robert-demarchy' },
        { num: 2, name: 'The Art Story — Pictorialism', url: 'https://www.theartstory.org/movement/pictorialism/' },
        { num: 3, name: 'SUNY New Paltz Dorsky Museum — Robert Demachy', url: 'https://www.newpaltz.edu/museum/collections/selections/robert-demachy/' },
        { num: 4, name: 'Metropolitan Museum of Art — Struggle (Demachy, Robert)', url: 'https://www.metmuseum.org/art/collection/search/289550' },
        { num: 5, name: 'Academia.edu — Robert Demachy: apostle of the gum bichromate process', url: 'https://www.academia.edu/29332945/Robert_Demachy_apostle_of_the_gum_bichromate_process_2015_' },
        { num: 6, name: 'Monovisions — Robert Demachy Biography', url: 'https://monovisions.com/robert-demachy-biography-pictorial-photographer/' },
      ]
    }
  },

  /* ─────────────────────────────────────────
     1910–1920s
     ───────────────────────────────────────── */
  {
    id: 'strand',
    name: 'Paul Strand',
    nameJa: 'ポール・ストランド',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1890–1976',
    gender: '男性',
    era: '1910',
    movements: ['ストレート写真', 'モダニズム', 'ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/artists/5722' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Paul_Strand' },
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/art/collection/search?q=paul+strand' },
    ],
    amazon: '',
    context: {
      text: 'ポール・ストランドが写真の転換を遂げた背景には、1907年にルイス・ハインに連れられて初めて訪れたギャラリー291での体験がある。セザンヌはリンゴや山などの自然物を「球・円柱・円錐の組み合わせ」として捉え直し、ピカソ・ブラックはそこからさらに踏み込んで対象を複数の視点から見た幾何学的平面に分解し、ひとつの画面上に再構成した——これが「形の構造的分解」である*1。ストランドが直感したのは、現実の世界にはすでにその幾何学が潜んでいるということだった。柵の縦板が刻むリズム、窓の格子が床に落とす平行四辺形の影、テラスに置かれたボウルが描く円弧と楕円——それらをシャープなフォーカスと高コントラストでそのまま写し取ることで、絵画のような筆触の模倣なしに純粋な構造的美を引き出せる。逆に言えば、ピクトリアリズムのソフトフォーカスや印画技法はそれらの幾何学をぼかして曖昧にするものであり、暗室での操作なく現実をありのままに写し取る「ストレート写真」こそが、この発見を実現できる方法だったのだ*1。1912年頃まで彼はピクトリアリズムの技法を実践していたが、この論理的な転換を経てシャープなフォーカスと大胆な幾何学的構成へと向かった。1916年のニューヨークで制作された「白い柵」「裏庭のボウル」は視点と形の純粋な相互作用のみを主題とし、同年のロウアーイーストサイドで撮影した「盲目の女」は、隠しプリズムレンズで被写体に気づかれずに正面から撮影した先駆的なストリートポートレートだった*2。これらはスティーグリッツ主宰の『カメラ・ワーク』最終号（第49–50号、1917年）に掲載され、「これまで写真界に現れた最も直接的で最も率直な仕事」と評された。「カメラという道具のもつ、絵画とは関係しながらも絵画を侵犯しない、純粋かつ知性的な使用」というストランド自身の言葉がストレート写真の宣言として後世に引用される*3。第一次世界大戦中は軍の医療部門でX線技師として従軍し、戦後にチャールズ・シェラーとのドキュメンタリー映画「マンハッタ」（1921年）を発表。1930年代はメキシコに招かれてムラリスモ政府文化局の映画部門を率い、農地改革を主題とした映画「波」（1936年）を制作した*4。その後ニューメキシコ・ニューイングランド・フランス・イタリア・ガーナなど各地で農民の生活を記録し続け、「時代を超えた普遍的な人間の尊厳の記録」という一貫した主題のもとで半世紀以上にわたる制作を続けた。1936年にはニューヨーク写真リーグを支援し、社会変革を写真で実践するという理念を次世代に継承した*5。彼の1916–17年の仕事は写真が絵画の模倣を脱して独自の表現媒体として自立した歴史的転換点であり、アンセル・アダムズ・エドワード・ウェストンらに受け継がれたアメリカ「ストレート写真」の直接の源流とされている。スティーグリッツがピクトリアリズムからの脱却を主導したとすれば、ストランドはその脱却の具体的な方法論を実証した写真家だった*3。',
      citations: [
        { num: 1, name: 'The Art Story — Paul Strand', url: 'https://www.theartstory.org/artist/strand-paul/' },
        { num: 2, name: 'Metropolitan Museum of Art — Paul Strand', url: 'https://www.metmuseum.org/toah/hd/strn/hd_strn.htm' },
        { num: 3, name: 'Smarthistory — Paul Strand, White Fence', url: 'https://smarthistory.org/paul-strand-white-fence/' },
        { num: 4, name: 'George Eastman Museum — Paul Strand', url: 'https://www.eastman.org/collections/photography/strand-paul' },
        { num: 5, name: 'AnOther Magazine — Paul Strand', url: 'https://www.anothermag.com/art-photography/11173/paul-strand-radical-political-art' }
      ]
    }
  },

  {
    id: 'coburn',
    name: 'Alvin Langdon Coburn',
    nameJa: 'アルヴィン・ラングドン・コバーン',
    nationality: 'US / GB',
    flag: '🇺🇸',
    years: '1882–1966',
    gender: '男性',
    era: '1910',
    movements: ['モダニズム', 'ヴォルテクシズム', '実験的技法'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Alvin_Langdon_Coburn' },
      { label: 'Tate — Vortograph', url: 'https://www.tate.org.uk/art/artworks/coburn-vortograph-p04469' },
    ],
    amazon: '',
    context: {
      text: 'ボストン生まれのアルヴィン・ラングドン・コバーンは17歳で写真家フレデリック・H・デイに師事して写真を学び、1902年にスティーグリッツの写真分離派に参加した。ロンドンとニューヨークを行き来しながら都市の高所からの俯瞰写真や著名人の肖像（ロダン・マーク・トウェイン・バーナード・ショウら）を制作し、写真集「ロンドン」（1909年）・「ニューヨーク」（1910年）でピクトリアリズムの優れた実践者として名声を得た*1。転機は1916–17年にエズラ・パウンドおよびウィンダム・ルイスのヴォルテクシズム運動と交流したことにある。ヴォルテクシズムは機械と運動のエネルギーを芸術に取り込もうとしたイギリスの前衛運動だった。第一次世界大戦中の閉塞した創作環境の中で、コバーンは既存の対象を「そのまま写す」ことへの限界を感じた*2。そこで三枚の金属鏡を正三角柱に配置した万華鏡装置「ヴォルトスコープ」を自作し、レンズ前方に装着することで被写体を幾何学的抽象パターンへと変換して撮影する技法を開発した。1917年2月のロンドン・カメラ・クラブで発表した「ヴォルトグラフ」18点は、写真史上最初の純粋抽象写真の展覧会として記録されている*3。パウンドは「カメラは現実から解放された！」と評し、美術史家キース・F・デイヴィスは「完全な抽象を意図した最初の写真群」と位置づけた*4。しかしコバーンはその後まもなく神智学・フリーメーソンに専心して写真から離れ、北ウェールズに隠棲した。この短命な実験は、ピクトリアリストとして成功した写真家が表象の限界に突き当たり、装置の変換によって「見ること」の概念そのものを問い直した試みとして後世に再評価されている*5。',
      citations: [
        { num: 1, name: 'Royal Photographic Society — Alvin Langdon Coburn', url: 'https://rps.org/about/collections/coburn/' },
        { num: 2, name: 'PhotoAnthology — Coburn and Vorticism', url: 'https://photoanthology.com/alvin-langdon-coburn/' },
        { num: 3, name: 'MoMA — Vortograph', url: 'https://www.moma.org/collection/works/46633' },
        { num: 4, name: 'George Eastman Museum — Coburn', url: 'https://www.eastman.org/collections/photography/coburn-alvin-langdon' },
        { num: 5, name: 'Tate — Vortograph (Ezra Pound)', url: 'https://www.tate.org.uk/art/artworks/coburn-vortograph-p04469' }
      ]
    }
  },

  {
    id: 'manray',
    name: 'Man Ray',
    nameJa: 'マン・レイ',
    nationality: 'US / FR',
    flag: '🇺🇸',
    years: '1890–1976',
    gender: '男性',
    era: '1910',
    movements: ['ダダ', 'シュルレアリスム', 'レイオグラフ'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/artists/3787' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Man_Ray' },
      { label: 'Tate', url: 'https://www.tate.org.uk/art/artists/man-ray-1542' },
    ],
    amazon: '',
    context: {
      text: 'フィラデルフィア生まれのエマニュエル・ラドニツキー（マン・レイ）が写真実践に転じた最大の契機は、1913年のアーモリーショーでマルセル・デュシャンの作品と出会い、その後親交を深めたことにある。デュシャンの「レディメイド」概念——既製品を提示するだけで芸術になるという考え——は、「写真は芸術を記録するためではなく、それ自体が思考のツールになりうる」という発想をマン・レイに与えた*1。第一次世界大戦の大量殺戮に幻滅したダダイストたちは、理性・進歩・国家・既成芸術の権威をすべて解体しようとした。マン・レイはその写真的実践を担う一人として1921年にパリへ移住し、アンドレ・ブルトン率いるシュルレアリスムに合流した*2。同年、暗室で作業中に印画紙の上にうっかり物を置いたまま光を当てたことで、カメラを使わずに物の影を直接感光紙に焼き付ける技法を「発見」した。これを「レイオグラフ」と命名し、詩人トリスタン・ツァラは「物体が夢を見る瞬間」と評した*3。レイオグラフはネガが存在しない一点ものであり、物と光の直接的な接触の痕跡という性格がシュルレアリスムの「偶然性」と「無意識の表出」への関心と完全に呼応した。1929年にはアシスタントのリー・ミラーの暗室操作の失敗から「ソラリゼーション」（明暗部分反転）技法を開発し、以後これを多くの写真やポートレートに応用した*4。ファッション誌ヴォーグ・ヴァニティ・フェアへの写真提供は生活費を賄いつつも、前衛芸術家が商業メディアにどこまで応じるかという緊張を体現した存在でもあった。第二次世界大戦中はロサンゼルスへ避難し、戦後パリに戻って制作を継続した*5。マン・レイの実践は「写真とは何かを記録するためではなく、何かを出現させる装置だ」という観点の礎となり、カメラレス写真・ソラリゼーション・多重露光など暗室技法の実験的可能性を20世紀全体を通じて探究した後継者たちに影響を与え続けた。その根底にあったのは「制作行為における偶然の積極的受容」というダダ以来の問いだった*6。',
      citations: [
        { num: 1, name: 'The Art Story — Man Ray', url: 'https://www.theartstory.org/artist/man-ray/' },
        { num: 2, name: 'Metropolitan Museum of Art — Man Ray', url: 'https://www.metmuseum.org/toah/hd/manr/hd_manr.htm' },
        { num: 3, name: 'Tate — Man Ray', url: 'https://www.tate.org.uk/art/artists/man-ray-1542' },
        { num: 4, name: 'MoMA — Man Ray Rayographs', url: 'https://www.moma.org/artists/3787' },
        { num: 5, name: 'Philadelphia Museum of Art — Man Ray', url: 'https://www.philamuseum.org/collection/object/89165' },
        { num: 6, name: 'Artsper — Man Ray Biography', url: 'https://www.artsper.com/en/contemporary-artists/france/1085/man-ray' }
      ]
    }
  },

  {
    id: 'moholy',
    name: 'László Moholy-Nagy',
    nameJa: 'ラースロー・モホイ＝ナジ',
    nationality: 'HU / DE',
    flag: '🇭🇺',
    years: '1895–1946',
    gender: '男性',
    era: '1910',
    movements: ['バウハウス', '新しいヴィジョン', 'レイオグラフ', '実験的技法'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/artists/4016' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/L%C3%A1szl%C3%B3_Moholy-Nagy' },
      { label: 'Bauhaus-Archiv', url: 'https://www.bauhaus.de/en/sammlung/6574_laszlo_moholy_nagy/' },
    ],
    amazon: '',
    context: {
      text: 'ハンガリー生まれのラースロー・モホイ＝ナジは第一次世界大戦に従軍し、塹壕の中で独学でデッサンを始めた。戦後ベルリンでロシア構成主義・ダダと接触し、「芸術は社会変革の工具でなければならない」という信念を持つようになった*1。1923年にヴァルター・グロピウスに招かれてバウハウスの金属工房マイスターに就任すると、写真・映画・印刷をデザイン教育の中心に組み込み始めた。1925年の著書『絵画・写真・映画』では「写真の問題は写真らしい写真を作ることではなく、いかに人間の視知覚を拡張するかにある」と論じた。同書は「光で描くことができれば、まずそれを試みよ。絵筆は不要だ」という視点から、印刷・ポスター・書籍デザインにいたる視覚メディア全体を射程に収めた革命的な教科書だった*2。モホイ＝ナジが推進した「新しいヴィジョン」の核心は、「見慣れたものを見知らぬものとして提示する」という認識論的革新にあった——真上からの俯瞰・真下からの仰角・極端なクローズアップ・放射状の光と影など、通常の人間視点には存在しない角度からの提示が認識そのものを刷新するという考え方だ*3。フォトグラム（暗室での物体の直接感光）はマン・レイと独立に実践し、「純粋な光の構成」として体系化した。1930年には鉄骨と透明素材にモーターを組み込んだ「光・空間調整装置」を完成させ、その映像記録「光のディスプレイ」（1930年）も発表した*4。「今日、写真を読めない者は文盲と同じだ」という言葉は視覚リテラシーを20世紀教育の根本問題として定式化した*5。1933年のナチス政権樹立でバウハウスは閉校となり、モホイ＝ナジはロンドンを経て1937年にシカゴへ移住し「ニュー・バウハウス（現イリノイ工科大学デザイン学部）」を設立した。死後1947年に刊行された遺著『動体視力』はデザイン教育の基本文献となり、彼が持ち込んだ「見ることを教える」という教育哲学は戦後の商業デザイン・広告写真・建築写真に広範な影響を及ぼした*6。「形の知覚そのものを教育で変えられる」というモホイ＝ナジの確信は、現代デザイン教育の中心原理として今日も継承されている。',
      citations: [
        { num: 1, name: 'Tate — László Moholy-Nagy', url: 'https://www.tate.org.uk/art/artists/laszlo-moholy-nagy-1599' },
        { num: 2, name: 'Metropolitan Museum of Art — Moholy-Nagy', url: 'https://www.metmuseum.org/toah/hd/moho/hd_moho.htm' },
        { num: 3, name: 'Bauhaus-Archiv — Moholy-Nagy', url: 'https://www.bauhaus.de/en/sammlung/6574_laszlo_moholy_nagy/' },
        { num: 4, name: 'MoMA — László Moholy-Nagy', url: 'https://www.moma.org/artists/4016' },
        { num: 5, name: 'Art History Unstuffed — Moholy-Nagy and the New Vision', url: 'https://www.arthistoryunstuffed.com/moholy-nagy-new-vision/' },
        { num: 6, name: 'IIT Institute of Design — History', url: 'https://id.iit.edu/about/history/' }
      ]
    }
  },

  {
    id: 'sander',
    name: 'August Sander',
    nameJa: 'アウグスト・ザンダー',
    nationality: 'DE',
    flag: '🇩🇪',
    years: '1876–1964',
    gender: '男性',
    era: '1910',
    movements: ['新即物主義', '社会ドキュメンタリー', 'ポートレート'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/artists/5180' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/August_Sander' },
      { label: 'Tate', url: 'https://www.tate.org.uk/art/artists/august-sander-1860' },
    ],
    amazon: '',
    context: {
      text: 'アウグスト・ザンダーが「20世紀の人々」という組織的肖像プロジェクトを構想するに至った根拠には、20世紀初頭のドイツで科学的信頼性をもっていた「人相学」への関心があった。職業・社会的立場・生活環境が身体と顔に刻印されるという考え方のもとで、ザンダーはヴェスターヴァルト地方の農民を繰り返し撮影し「人物の外見から社会構造を可視化できる」という確信を深めた*1。プロジェクトは農民→職人→女性→階級と職業→芸術家→都市→最後の人々という7つのグループで構成され、全体で数百点のポートレートから成る「人類学的アーカイブ」として構想された。その最初の公開が1929年刊行の写真集『時代の顔』（45点収録）であり、序文を書いた小説家アルフレート・デーブリンは「文字のない社会学だ」と評した*2。ヴァイマール共和国期の「新即物主義」の画家たち——オットー・ディックスやゲオルク・グロスが感傷を排した冷徹な視点でヴァイマール社会を描いたのと同じ姿勢が、ザンダーのポートレートにもあった*3。ヴァイマール時代のドイツには「社会的に周縁化された人々をいかに表象するか」という議論が渦巻いており、ザンダーのプロジェクトはその文脈の中で「非評価的・非感傷的な記録」の可能性を示した試みでもあった。1934年、ナチス政権は息子エーリッヒ（反ナチ活動で逮捕・1944年獄死）への圧力として『時代の顔』の残部を没収・廃棄し、ゲシュタポの捜索でガラス乾板の一部が押収・破壊された*4。ザンダー自身は戦争を生き延びたが1946年のケルン・アトリエ火災でさらに多くの資料を失った。1950–60年代の写真史再評価でジョン・ザルコウスキー（MoMA）らが「ポートレートが社会の証言になりうる」という先駆的実践として再発見し、ダイアン・アーバスのアウトサイダー・ポートレートへの影響が指摘されている*5。またベッヒャー夫妻による工業建築の類型的記録にもザンダーの「社会の全体を体系的に記録する」という方法論の継承が認められる。「写真家は絵を描くのではなく、社会の証人でなければならない」という彼の言葉は、ドキュメンタリー写真の倫理的根拠として今日も引用される*6。',
      citations: [
        { num: 1, name: 'Metropolitan Museum of Art — August Sander', url: 'https://www.metmuseum.org/toah/hd/sand/hd_sand.htm' },
        { num: 2, name: 'Tate — August Sander Research Papers', url: 'https://www.tate.org.uk/research/publications/tate-papers/14/august-sander-people-of-the-twentieth-century' },
        { num: 3, name: 'Hauser & Wirth — August Sander', url: 'https://www.hauserwirth.com/artists/2822-august-sander/' },
        { num: 4, name: 'MoMA — August Sander', url: 'https://www.moma.org/artists/5180' },
        { num: 5, name: 'George Eastman Museum — August Sander', url: 'https://www.eastman.org/collections/photography/sander-august' },
        { num: 6, name: 'Apollo Magazine — August Sander', url: 'https://www.apollo-magazine.com/august-sander-people-of-the-twentieth-century/' }
      ]
    }
  },

  {
    id: 'renger',
    name: 'Albert Renger-Patzsch',
    nameJa: 'アルベルト・レンガー＝パッチュ',
    nationality: 'DE',
    flag: '🇩🇪',
    years: '1897–1966',
    gender: '男性',
    era: '1910',
    movements: ['新即物主義', 'モダニズム'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Albert_Renger-Patzsch' },
      { label: 'J. Paul Getty Museum', url: 'https://www.getty.edu/art/collection/artist/2038' },
      { label: 'Tate', url: 'https://www.tate.org.uk/art/artists/albert-renger-patzsch-1814' },
    ],
    amazon: '',
    context: {
      text: 'アルベルト・レンガー＝パッチュは1920年代のドイツで、ピクトリアリズムとバウハウス系実験写真の双方に距離を置く第三の路線を切り開いた。ピクトリアリズムが写真を絵画的に「美化」し、バウハウスが写真を視知覚変革の道具とみなしたのに対し、レンガー＝パッチュは「物それ自体の構造的な美しさをそのまま示す」という立場をとった*1。1928年刊行の写真集は工場の煙突・鉄道橋・植物の細部・陶磁器の反射・鋳物工具など100点を収録したものだが、本人が意図したタイトルは「物」であり、出版社エルンスト・ヴァスムートが商業的理由から「世界は美しい（Die Welt ist schön）」に変更したという経緯がある*2。この刊行は批評家ヘルムート・ゲルンスハイムが「ドイツ近代写真の転換点」と評し、トーマス・マンは公開の場で絶賛した*3。ヴァルター・ベンヤミンは1931年の論考「写真の小史」で「物に宇宙的な意味を持たせることができるが、人間の社会的条件については沈黙している」と批判した——政治的・社会的文脈を排した「物の美しさ」への集中への正面からの異議申し立てだった*4。レンガー＝パッチュが実践した「物の写真」は対象の形・質感・光を最大限の技術的精度で記録する手法であり、ザンダーが社会の総体を記録しようとしたのに対し、個別の事物の視覚的純度にこだわった点で対照的だった。1944年の連合軍爆撃でゾースト近郊のアトリエが壊滅しコレクションの大部分を失ったが、戦後はルール地方の鉱山・製鉄所を精力的に撮影し続けた*5。彼のアプローチはドイツ産業写真・製品広告の美学的基盤となり、ベッヒャー夫妻による工業建築の類型的記録の源流の一つとして位置づけられている*6。',
      citations: [
        { num: 1, name: 'Aperture — Albert Renger-Patzsch', url: 'https://aperture.org/editorial/albert-renger-patzsch/' },
        { num: 2, name: 'J. Paul Getty Museum — Renger-Patzsch', url: 'https://www.getty.edu/art/collection/artist/2038' },
        { num: 3, name: 'George Eastman Museum — Renger-Patzsch', url: 'https://www.eastman.org/collections/photography/renger-patzsch' },
        { num: 4, name: 'Tate — Albert Renger-Patzsch', url: 'https://www.tate.org.uk/art/artists/albert-renger-patzsch-1814' },
        { num: 5, name: 'PhotoAnthology — Albert Renger-Patzsch', url: 'https://photoanthology.com/albert-renger-patzsch/' },
        { num: 6, name: 'UGA Esploro — Renger-Patzsch and Neue Sachlichkeit', url: 'https://esploro.libs.uga.edu/esploro/outputs/graduate/The-New-Objectivity-photography-of-Albert/9949333614902959' }
      ]
    }
  },
  /* ─────────────────────────────────────────
     1930–1940s
     ───────────────────────────────────────── */

  {
    id: 'lange',
    name: 'Dorothea Lange',
    nameJa: 'ドロシア・ラング',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1895–1965',
    gender: '女性',
    era: '1930',
    movements: ['FSA写真', '社会ドキュメンタリー', 'ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/artists/3373' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Dorothea_Lange' },
      { label: 'Library of Congress', url: 'https://guides.loc.gov/migrant-mother' },
    ],
    amazon: '',
    context: {
      text: 'ドロシア・ラングはサンフランシスコで商業ポートレートスタジオを経営していたが、1932年の大恐慌の絶頂期に、スタジオの窓から路上の失業者行列を見て外に飛び出したことがドキュメンタリー写真への転換点となった。1935年に連邦農業安定局（FSA）のロイ・ストライカーに雇用され、農村の貧困記録を担う写真家となった*1。FSAは農村の困窮を可視化してニューディール政策への支持を喚起する証拠写真を集めることを使命としており、ラングはカリフォルニア州各地の移住農業労働者キャンプを記録した。1936年3月、ニポモのエンドウ豆労働者キャンプで5〜6枚の連続撮影を行い、フローレンス・オーウェンズ・トンプソン（チェロキー族、当時32歳）とその子どもたちを捉えた一枚が「移住者の母」となった。ラングが記した詳細なキャプション——「食料なしに7人の子どもを抱え、野菜と子どもたちが捕まえた鳥で生き延びている」——とともに『サンフランシスコ・ニュース』紙（1936年3月10日付）に掲載され、連邦政府はキャンプに20,000ポンドの食糧を緊急輸送した*2。この写真はMoMAが1941年に「ドキュメンタリーの傑作」として評価し、大恐慌を象徴する一枚として世界的に知られる。ラングはトンプソンの名前も経歴も記録せず、撮影後すぐに写真を連邦政府への提出前に新聞社へ送った——トンプソンは後に「写真を売らないと言っていた」と証言しており、ラングが交わしたとされる約束の不履行が問題となった*3。撮影された写真は連邦政府委託のため著作権が発生せず、ラングにもトンプソンにも対価は一切支払われなかった。トンプソンは「あの写真から一銭も得られなかった」と語り、自分の名前が判明したのは撮影から42年後の1978年のことだった*3。政府の委嘱を受けた写真家と、貧困ゆえに撮影を断る選択肢を持ちにくかった被写体との非対称な関係、そして対価も名誉も伴わないまま肖像が国家プロパガンダとして流通した構造は、ドキュメンタリー写真における被写体の権利・同意・利益配分という問題を先駆的に提起したケースとして今日も論じられる*3。1942年には大統領令9066号による日系人強制収容を陸軍省から記録する任務を受けたが、当局はその写真を機密扱いとして封印し、存命中には公開されなかった*4。1965年にMoMAで大規模な回顧展が準備されたが、ラングは同年66歳でその開幕を見ることなく死去した。「移住者の母」は一枚の写真が政府の政策決定に直接影響を与えた稀有な例として写真史に記録されており、写真がプロパガンダ手段として機能しながら被写体の人間的尊厳を記録するという二重の役割の複雑さを体現した作品である。この複雑さはドキュメンタリー写真の倫理的基盤について今日も議論を呼び続けている*5。彼女が実践した「被写体が語り、写真家は聴く」という撮影倫理は、現代のドキュメンタリー写真実践の倫理的基盤の一つとして継承されている。',
      citations: [
        { num: 1, name: 'Museum of Contemporary Photography — Dorothea Lange and the Documentary Tradition', url: 'https://www.mocp.org/resources/dorothea-lange-and-the-documentary-tradition/' },
        { num: 2, name: 'Library of Congress — Migrant Mother Research Guide', url: 'https://guides.loc.gov/migrant-mother' },
        { num: 3, name: 'JSTOR Daily — Dorothea Lange and the Making of Migrant Mother', url: 'https://daily.jstor.org/dorothea-lange-and-the-making-of-migrant-mother/' },
        { num: 4, name: 'Smarthistory — Dorothea Lange, Migrant Mother', url: 'https://smarthistory.org/dorothea-lange-migrant-mother/' },
        { num: 5, name: 'LA Review of Books — Migrant Mother: Dorothea Lange and the Truth of Photography', url: 'https://lareviewofbooks.org/article/migrant-mother-dorothea-lange-truth-photography/' }
      ]
    }
  },

  {
    id: 'evans',
    name: 'Walker Evans',
    nameJa: 'ウォーカー・エヴァンス',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1903–1975',
    gender: '男性',
    era: '1930',
    movements: ['FSA写真', 'ドキュメンタリー', 'ストリート写真'],
    thumbnail: '',
    links: [
      { label: 'Metropolitan Museum of Art', url: 'https://www.metmuseum.org/essays/walker-evans-1903-1975' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Walker_Evans' },
      { label: 'ICP', url: 'https://www.icp.org/browse/archive/constituents/walker-evans' },
    ],
    amazon: '',
    context: {
      text: 'ウォーカー・エヴァンズはFSA（農業安定局）のために1935–37年に南部を中心に農村の貧困を記録したが、同局の本来の使命——ニューディール政策宣伝のための写真提供——に対して意図的に距離を置いた。「プロパガンダ仕事にエヴァンズほど不向きな人物は想像しにくい」と当時から評されるほど、政治的メッセージより「アメリカの日常の本質的な蒸留」を追求し、8×10インチ大判カメラでの精密な構図と自然光のみで対象を記録した*1。指定された取材ルートも無視して個人的な主題——ガスステーション・理髪店の看板・ヴィクトリア朝建築など——を追い続けた。1938年、MoMAは写真家単独としては同館史上初となる個展「アメリカン・フォトグラフス」をエヴァンズに提供し、批評家リンカーン・カースタインの論文を添えた写真集を刊行した。これは写真を「ファインアート」として美術館が本格的に承認した最初期の出来事の一つとして写真史に記録されている*2。ジャーナリストのジェームズ・エイジーとアラバマ州の白人小作農三家族に同居して取材した成果は、雑誌に採用されず1941年にようやく書籍『今こそ有名な人々を称えよう』として出版された。当初は不評だったが1960年代の再刊以降は20世紀アメリカ文学の金字塔として評価が定まった*3。エヴァンズはキャプションなしで写真を提示することにこだわり、「写真集の各節末にだけ説明を記す」という形式を採用した——これは観者に先入観なく写真と向き合う機会を与える意図的な選択であり、写真が何かを語るためには文字の補助を必要としないという確信の表れだった。後年のニューヨーク地下鉄シリーズ（1938–41年撮影、1966年刊行）では、衣服の下に隠したカメラで乗客に気づかれずに撮影し、匿名の他者の顔に社会の断面を読み取ろうとした*4。1945年から20年間『フォーチュン』誌の写真編集者を務め、1965年にはイェール大学の写真教授に就任した。エヴァンズの写真が「詩的」と評される根拠は、操作や演出ではなく選択と構図にある。何を枠に収め何を切り落とすかという判断が、ガスステーションの看板・擦り切れた壁・小作農の顔を「現在が既に過去であるかのように見える」静けさで提示し、見慣れた日常に見過ごされていた普遍性を浮かび上がらせる——これをメトロポリタン美術館は「文学のリリシズム・アイロニー・叙述構造を写真に持ち込んだ」と評した*1。「文字通り、権威ある、超越的」という彼自身のスタイルの定義は記録の詩性という逆説を言語化したものであり、ロバート・フランク・リー・フリードランダーなど次世代アメリカ写真が継承した美学の源流となった*5。彼のFSA写真はその後ライブラリー・オブ・コングレスに永続保存されており、今日でも研究者・写真家に参照され続けている。',
      citations: [
        { num: 1, name: 'Metropolitan Museum of Art — Walker Evans (1903–1975)', url: 'https://www.metmuseum.org/essays/walker-evans-1903-1975' },
        { num: 2, name: 'International Center of Photography — Walker Evans', url: 'https://www.icp.org/browse/archive/constituents/walker-evans' },
        { num: 3, name: 'Smithsonian National Museum of American History — Walker Evans', url: 'https://americanhistory.si.edu/collections/object/nmah_1341035' },
        { num: 4, name: 'MoMA — Walker Evans', url: 'https://www.moma.org/artists/1777' },
        { num: 5, name: 'John&#39;s Chronicle — Walker Evans: Literate, Authoritative, Transcendent', url: 'https://johnschronicle.org/2018/12/17/walker-evans-literate-authoratative-transcendent/' }
      ]
    }
  },

  {
    id: 'cartierbresson',
    name: 'Henri Cartier-Bresson',
    nameJa: 'アンリ・カルティエ＝ブレッソン',
    nationality: 'FR',
    flag: '🇫🇷',
    years: '1908–2004',
    gender: '男性',
    era: '1930',
    movements: ['決定的瞬間', 'フォトジャーナリズム', 'ストリート写真'],
    thumbnail: '',
    links: [
      { label: 'Fondation HCB', url: 'https://www.henricartierbresson.org/en/hcb/biography/' },
      { label: 'Magnum Photos', url: 'https://www.magnumphotos.com/photographer/henri-cartier-bresson/' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Henri_Cartier-Bresson' },
    ],
    amazon: '',
    context: {
      text: 'アンリ・カルティエ＝ブレッソンは1926年からシュルレアリスム運動と接触し、ルネ・クルヴェルの紹介でアンドレ・ブルトンと出会った。シュルレアリスムの「現実の事物の中に潜む夢的な質を顕在化させる」という視点を写真に持ち込み、1931年にライカ35mmカメラを手にして以来、プリントの加工・トリミングを徹底して拒否し、ファインダーの中での形の構成と「一瞬の意味」の同時把握を唯一の制作原理とした*1。「ある事象の意味と、その事象を正確に組織する形の同時認識——これが一瞬のうちに起きる」という言葉が写真論の核心だ*2。1940年に独軍の捕虜となり、フランス中部ゲルスドルフ（現ドイツ）の収容所で3年間過ごし、3度目の試みで1943年に脱走した。帰国後、パリ解放（1944年）を記録するとともにジャン・ルノワールのアシスタントとして映画にも関わった。1947年にロバート・キャパ・デイヴィッド・シーモア（シム）・ジョージ・ロジャー・ウィリアム・ヴァンディヴァートとともにマグナム・フォトを共同設立した。マグナムは写真家が自分の作品の著作権と編集権を保持できる初のフォト・エージェンシーであり、「どの雑誌からも独立したまま世界の重要な出来事を伝える」という理念のもとで設立された*3。1952年刊行のフランス語版写真集『逃げ去るイメージ』は英語版で『決定的瞬間』と題され、表紙はアンリ・マティスがデザインした。マグナムの一員としてインド独立（1947年）・ガンジー暗殺（1948年）・中国共産革命（1948年）などを取材し、戦後フォトジャーナリズムの美学的・倫理的基準を確立した*4。1955年にルーヴル美術館での写真展示を初めて許可された最初の写真家となり、写真のファインアート化を象徴する存在となった。1975年以降は写真制作をほぼ停止してデッサンと絵画に専念し、「写真家は常に何かを奪っている。絵は与えることだ」と語ったとされる。2003年には財団をパリに設立し、作品の恒久的な保存と公開の場を確保した*5。彼が示した「技術的精度より瞬間の詩性」という写真観は、世界中のストリートフォトグラファーに継承され続けている。フラッシュを一切使わないという彼の信念は「人工光は瞬間の詩性を殺す」という考えに基づいており、自然光と瞬間の倫理を生涯貫いた。',
      citations: [
        { num: 1, name: 'The Art Story — Henri Cartier-Bresson', url: 'https://www.theartstory.org/artist/cartier-bresson-henri/' },
        { num: 2, name: 'Aesthetics of Photography — Henri Cartier-Bresson', url: 'https://aestheticsofphotography.com/henri-cartier-bresson/' },
        { num: 3, name: 'International Center of Photography — Cartier-Bresson', url: 'https://www.icp.org/browse/archive/constituents/henri-cartier-bresson' },
        { num: 4, name: 'Fondation Henri Cartier-Bresson', url: 'https://www.henricartierbresson.org/en/hcb/' },
        { num: 5, name: 'Magnum Photos — Henri Cartier-Bresson', url: 'https://www.magnumphotos.com/photographer/henri-cartier-bresson/' }
      ]
    }
  },

  {
    id: 'capa',
    name: 'Robert Capa',
    nameJa: 'ロバート・キャパ',
    nationality: 'HU',
    flag: '🇭🇺',
    years: '1913–1954',
    gender: '男性',
    era: '1930',
    movements: ['戦争写真', 'フォトジャーナリズム'],
    thumbnail: '',
    links: [
      { label: 'Magnum Photos', url: 'https://www.magnumphotos.com/photographer/robert-capa/' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Robert_Capa' },
      { label: 'ICP', url: 'https://www.icp.org/browse/archive/constituents/robert-capa' },
    ],
    amazon: '',
    context: {
      text: 'ロバート・キャパはブダペスト生まれのアンドレ・フリードマンが1933年のパリで作り上げたペルソナだった。反政府活動を理由に17歳でハンガリーを追われ、ベルリンで写真エージェンシー（デフォト）のアシスタントとして暗室技術と取材術を学んだのち、ナチス台頭を避けてパリに移った。外国人フリーランスとして写真を高値で売るための戦略として、「著名なアメリカ人写真家ロバート・キャパ」という架空の人物像を当時の恋人ゲルダ・タローと共謀して作り上げた*1。1936年のスペイン内戦取材中に撮影した「崩れ落ちる兵士」は、共和国軍民兵フェデリコ・ボレル・ガルシアが銃弾を受けて崩れ落ちる瞬間とされ、『ヴュ（Vu）』誌掲載後にキャパを国際的に知らしめ、1938年英国の『ピクチャー・ポスト』誌が「世界最高の戦場写真家」と呼んだ*2。写真が実際の戦闘中に撮影されたかどうかについての論争は今日まで続いている。1944年6月6日のノルマンディー上陸作戦（オマハ・ビーチ）では4本のフィルムを撮影してロンドンに持ち帰ったが、現像を急いだ担当者が乾燥温度を誤り、フィルムの大部分が熱で溶けて11コマのみが残存した。『ライフ』誌（1944年6月19日号）はこれを「興奮で手が震えた」と説明したが、キャパ自身はその説明を否定した*3。1947年にカルティエ＝ブレッソン・デイヴィッド・シーモア・ジョージ・ロジャーとともにマグナム・フォトを設立した。「雑誌の需要に縛られない、写真家が著作権を保持する協同組合」という構想はキャパが主導し、パリとニューヨークにオフィスを置く国際的な組織として発足した*4。「写真が十分に良くなければ、あなたは被写体に十分近づいていない」という言葉は戦場写真の方法論と倫理を語る格言となった。スペイン内戦・日中戦争・第二次世界大戦・第一次中東戦争・第一次インドシナ戦争と5つの戦争を取材した。1954年5月25日、北ベトナムのタイビン省での取材中に地雷を踏んで40歳で死亡した。1966年にキャパの遺志を継いで設立された国際写真センター（ICP）は「ロバート・キャパ金メダル賞」を設けており、これは今日も戦場・報道写真分野における最高の国際賞の一つとして継続されている*5。キャパの死後に発見された「メキシコのスーツケース」（2007年）にはスペイン内戦時の約4500枚の未知のネガが含まれていた。',
      citations: [
        { num: 1, name: 'The Art Story — Robert Capa', url: 'https://www.theartstory.org/artist/capa-robert/' },
        { num: 2, name: 'Metropolitan Museum of Art — The Falling Soldier', url: 'https://www.metmuseum.org/art/collection/search/283315' },
        { num: 3, name: 'Head On Photo Festival — Robert Capa D-Day', url: 'https://headon.org.au/magazine/robert-capa-and-the-story-behind-his-iconic-d-day-pictures' },
        { num: 4, name: 'Magnum Photos — Robert Capa', url: 'https://www.magnumphotos.com/photographer/robert-capa/' },
        { num: 5, name: 'International Center of Photography — This Is War! Robert Capa at Work', url: 'https://www.icp.org/sites/default/files/exhibition/credits/sites/default/files/exhibition_pdfs/rcapa_press.pdf' }
      ]
    }
  },

  {
    id: 'domon',
    name: 'Ken Domon',
    nameJa: '土門拳',
    nationality: 'JP',
    flag: '🇯🇵',
    years: '1909–1990',
    gender: '男性',
    era: '1930',
    movements: ['社会ドキュメンタリー', 'リアリズム写真', '日本写真'],
    thumbnail: '',
    links: [
      { label: '土門拳記念館', url: 'http://www.domonken-kinenkan.jp/' },
      { label: 'Wikipedia (JA)', url: 'https://ja.wikipedia.org/wiki/%E5%9C%9F%E9%96%80%E6%8B%B3' },
      { label: 'Artscape', url: 'https://artscape.jp/artword/index.php/%E5%9C%9F%E9%96%80%E6%8B%B3' },
    ],
    amazon: '',
    context: {
      text: '土門拳が戦後に提唱した「リアリズム写真」は、戦前のサロン写真（技巧的な美的追求）と、自身が戦時中に携わったプロパガンダ写真報道への反省から生まれた。「カメラとモチーフの直結」と「絶対非演出の絶対スナップ」を原理として、社会の現実と人間の生を加工・演出なしに提示することが写真の使命だと主張した*1。1950年から写真誌「カメラ」の月例審査員として多数のアマチュア写真家を指導し、その思想に共鳴した写真家群からは川田喜久治・東松照明・深瀬昌久らが育った*2。1955年に「リアリズム第一段階の終了」を宣言し、より深い主題性を持つ「第二段階」への移行として広島の原爆被害者記録に着手した。1957年から1年間にわたって広島の原爆病院・障害者施設・孤児院を「取り憑かれたように」取材し、5,800枚のネガから171点を収録した写真集『ヒロシマ』（1958年、研光社）を刊行した。国内外で大きな反響を呼び、戦後日本のドキュメンタリー写真の頂点とされる*3。同年代の写真集『筑豊のこどもたち』（1960年）は炭鉱地帯で生きる子どもたちの貧困を記録し、100円の廉価版として10万部が売れ、日本ジャーナリスト会議賞（第3回）を受賞した。『古寺巡礼』（美術出版社、1963–75年）は奈良・法隆寺・薬師寺などの仏像を大判カメラと多灯フラッシュで撮影した生涯の仕事となった。「日本文化とは何か」「日本人とは何か」という問いを写真で問い続けたこの仕事は、1968年に脳卒中で倒れた後も車椅子での制作を続けることで完成された*4。土門がリアリズム写真運動を通じて育てた写真家たちは、1960–70年代の日本写真の黄金時代を形成し、山形県酒田市に1983年に開館した土門拳記念館はその全作品を収蔵している*5。',
      citations: [
        { num: 1, name: '土門拳記念館 — 土門拳とその作品（戦後）', url: 'http://www.domonken-kinenkan.jp/domonken/sengo/' },
        { num: 2, name: 'nippon.com — 「鬼」と呼ばれた写真家・土門拳', url: 'https://www.nippon.com/ja/images/i00058/' },
        { num: 3, name: 'shashasha — Ken Domon', url: 'https://www.shashasha.co/en/artist/ken-domon' },
        { num: 4, name: '九州芸文館 — 土門拳の古寺巡礼展', url: 'https://www.kyushu-geibun.jp/main/1833.html' },
        { num: 5, name: '土門拳記念館', url: 'http://www.domonken-kinenkan.jp/domonken/' }
      ]
    }
  },

  {
    id: 'eugenesmith',
    name: 'W. Eugene Smith',
    nameJa: 'W・ユージン・スミス',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1918–1978',
    gender: '男性',
    era: '1930',
    movements: ['戦争写真', '社会ドキュメンタリー', 'フォトジャーナリズム'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/W._Eugene_Smith' },
      { label: 'ICP', url: 'https://www.icp.org/browse/archive/constituents/w-eugene-smith' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/W-Eugene-Smith' },
    ],
    amazon: '',
    context: {
      text: 'W・ユージン・スミスは1948年から1956年にかけて『ライフ』誌でフォト・エッセイという形式を確立した。従来の報道写真が「決定的瞬間の一枚」を追うものだったのに対し、スミスは数週間〜数年にわたって被写体の生活に同居し、被写体との関係を深めながら撮影した大量のカットを導入・展開・結末のある物語として編集するという長編ストーリーテリングの手法を採った*1。「ジャーナリズムから最初に消したい言葉は客観性だ」と述べたスミスにとって、フォト・エッセイは事実の羅列でなく「告発の叫び」として機能するものだった*3。1948年刊行の「カントリー・ドクター」はコロラド州の農村医師アーネスト・チェリアーニの日常を12日間追ったもので、写真ジャーナリズム史上最初の本格的なフォト・エッセイとして評価されている*1。スミスは「写真の使用方法に関する編集権」を巡って『ライフ』誌と繰り返し衝突し、計2度退社した。1955年にマグナムに参加し、ピッツバーグを主題とした大規模な都市記録プロジェクトに着手。当初3カ月の契約だったが3年間に延長され、17,000点の写真とオーディオ記録を残した*2。1971年、水俣病患者の家族からの連絡を受けてアイリーン・三重子とともに水俣市に移住し、当初3カ月の予定だった滞在が3年に及んだ。水銀汚染による神経障害を全身に負った胎児性水俣病患者の桐野智子を風呂に入れる母の写真「入浴する智子と母」は1972年に『ライフ』誌に掲載され、チッソの産業公害を世界に訴える象徴的な作品となった*3。1972年、チッソ幹部との交渉に患者家族と同行したスミスは、会社が雇った暴力団員に殴打されて意識を失い、右目の視力を永続的に損傷した。この暴行の事実は水俣病問題を国際的に広める契機となり、スミスの写真は裁判の証拠として機能し、チッソが被害者への損害賠償責任を負った日本初の公害訴訟の成立に寄与した*4。「真実を偏見とせよ」というスミスの言葉は、フォト・エッセイが単なる記録を超えて道徳的・政治的な主張になりうるという彼の立場を示している*5。',
      citations: [
        { num: 1, name: 'PetaPixel — W. Eugene Smith: Father of the Photo Essay', url: 'https://petapixel.com/2019/08/17/w-eugene-smith-master-of-the-editorial-photo-essay/' },
        { num: 2, name: 'International Center of Photography — W. Eugene Smith', url: 'https://www.icp.org/browse/archive/constituents/w-eugene-smith' },
        { num: 3, name: 'The Phoblographer — W. Eugene Smith: How Minamata Ushered Moral Storytelling', url: 'https://www.thephoblographer.com/2024/08/16/w-eugene-smith-how-minamata-redefined-photojournalism-with-a-moral-purpose/' },
        { num: 4, name: 'Artsy — W. Eugene Smith, 101 Images from Minamata', url: 'https://www.artsy.net/artwork/w-eugene-smith-101-images-from-minamata' },
        { num: 5, name: 'Center for Creative Photography — W. Eugene Smith Archive', url: 'https://ccp.arizona.edu/collections/w-eugene-smith-archive' }
      ]
    }
  },

  /* ─────────────────────────────────────────
     1950–1960s
     ───────────────────────────────────────── */

  {
    id: 'robertfrank',
    name: 'Robert Frank',
    nameJa: 'ロバート・フランク',
    nationality: 'CH',
    flag: '🇨🇭',
    years: '1924–2019',
    gender: '男性',
    era: '1950',
    movements: ['アメリカ写真', 'ドキュメンタリー', 'ストリート写真'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Robert_Frank' },
      { label: 'ICP', url: 'https://www.icp.org/browse/archive/constituents/robert-frank' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/Robert-Frank' },
    ],
    amazon: '',
    context: {
      text: 'ロバート・フランクはスイス・ユダヤ系家庭にチューリッヒで生まれ、1947年にニューヨークへ移住してハーパーズ・バザーのファッション写真家として働き始めた。しかし自身の写真的衝動はファッションではなく、移民の外国人として見るアメリカの「表面の下」にあった*1。1954年、ウォーカー・エヴァンズの推薦状（「今日の若手写真家の中で最も才能がある」）を添えてグッゲンハイム・フェローシップに申請し採択され、2年間で28,000枚以上を撮影した。アーカンソー州では汚れた服と外国語なまりを理由に警察に数時間拘束されるなど、アウトサイダーとしての体験が写真の視点に深く刻まれた*2。28,000枚から83枚を選んで構成した写真集『アメリカン』は1958年にフランスで出版され、翌年の米国版序文をビート作家ジャック・ケルアックが担当した。ケルアックは「小さなカメラを持ったスイス人、控え目で感じのよいロバート・フランクは、フィルムにアメリカの悲しい詩を吸い取り、世界の悲劇的詩人の仲間入りを果たした」と書いた*3。当時の主要写真誌『ポピュラー・フォトグラフィー』は「無意味なブレ・粒子・泥んこの露出・酔っ払いのホリゾン・全般的な杜撰さ」と批判したが、評論家ショーン・オハガンは後年「20世紀で最も影響力のある写真集かもしれない」と評価した*4。フランクが拒んでいたのは、1950年代の『ライフ』誌が体現した「繁栄し健全なアメリカ」という楽観的なビジュアル言語——明るい露出・整った構図・国民的一体感を演出するグラビア写真——だった。フランクの目はその「表面の下」に潜む人種隔離・孤独・格差を、外国人ならではの距離感で掬い上げた*2。初出版時は不評だったが、1960年代に入り公民権運動やベトナム反戦の気運が高まる中で、アメリカ社会の矛盾を先取りしていた写真集として再評価が急進した。ICPは『アメリカン』を「写真史上最も革命的な写真集のひとつ」と位置づけており、ゲーリー・ウィノグランド・リー・フリードランダー・ダニー・リヨン・ジョエル・マイロウィッツら1960年代以降のストリート写真家たちにとっての「バイブル」となった*2。写真集刊行後はドキュメンタリー映画制作に移行し、ビート世代の作家・詩人たちとの共同作「プル・マイ・デイジー」（1959年）を制作した*5。',
      citations: [
        { num: 1, name: 'PBS NewsHour — Robert Frank: An Outsider Looking In', url: 'https://www.pbs.org/newshour/arts/robert-frank-an-outsider-looking-in' },
        { num: 2, name: 'Sotheby&#39;s — The Everlasting Influence of Robert Frank&#39;s The Americans', url: 'https://www.sothebys.com/en/articles/the-everlasting-influence-of-robert-franks-the-americans' },
        { num: 3, name: 'Aperture — Robert Frank: The Americans', url: 'https://aperture.org/books/robert-frank-the-americans/' },
        { num: 4, name: 'Artsy — How Robert Frank&#39;s The Americans Broke the Rules', url: 'https://www.artsy.net/article/artsy-editorial-robert-franks-the-americans-matters-today' },
        { num: 5, name: 'ArtNews — Robert Frank, Legendary Photographer and Filmmaker', url: 'https://www.artnews.com/art-news/news/robert-frank-photographer-dead-13204/' }
      ]
    }
  },

  {
    id: 'williamklein',
    name: 'William Klein',
    nameJa: 'ウィリアム・クライン',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1926–2022',
    gender: '男性',
    era: '1950',
    movements: ['ストリート写真', 'アメリカ写真', 'フォトジャーナリズム'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/William_Klein_(photographer)' },
      { label: 'ICP', url: 'https://www.icp.org/browse/archive/constituents/william-klein' },
    ],
    amazon: '',
    context: {
      text: 'ウィリアム・クラインはニューヨーク生まれだが、除隊後のパリでフェルナン・レジェのもとで絵画を学び、エルスワース・ケリーやジャック・ヤングマンらアメリカ人画家と交流した。1954年にヴォーグ誌のアート・ディレクター、アレクサンダー・リーバーマンの目に留まり、ニューヨーク帰任とともに同誌の写真家として招かれた*1。1954–56年のニューヨーク滞在中に撮影した写真をまとめた写真集『ニューヨーク、人生は善く、善くあなたのために』（1956年）は、フランスで刊行されプリ・ナダール賞（1957年）を受賞したが、米国の出版社はマンハッタンの汚い側面への視線を嫌って長年拒絶し続けた*2。クラインは高速フィルム・高コントラスト・粒子・ブレ・広角レンズ・挑発的な密着クローズアップという技法を、「欠点」としてではなく「都市のエネルギーを写真に転換する言語」として意図的に選択した。クライン自身は「カメラでしかできないこと——粒子、コントラスト、ブレ、歪んだフレーミングなど——を探求した。写真のルールは私には関係なかった。私は外からやってきた」と語っている*3。この姿勢はピクトリアリズムの「美しい絵」への志向とも、ドキュメンタリーの「中立的記録」という建前とも異なる第三の立場——写真家の主観・攻撃性・コメントを画面に刻み込む表現——を切り開くものだった。広角レンズを顔に押しつけるような密着クローズアップは被写体を圧迫・変形させ、「記録」でなく「衝撃」を意図したものであり、当時のギャラリーやメディアが「暴力的」と評した所以でもある*2。この写真集が「20世紀で最も重要な写真集の一つ」と位置づけられる根拠は、それがロバート・フランクの『アメリカン』（1958年）とともに、写真の技術的正確さを規範とする当時の主流に正面から反旗を翻した最初の写真集のひとつだったからであり、ICP・Artforum・ニューヨーク・タイムズなど複数の権威ある機関が「写真の正統派技法への反抗」の起点として繰り返し参照してきた*4。1955年からヴォーグ誌で10年間ファッション写真を担当し、モデルをスタジオから街頭に連れ出すという革新的な手法でファッション写真の概念を変えた。後年は映画監督としても活躍し、1966年に『フー・アー・ユー、ポリー・マグー？』を発表するなど多彩な活動を続け、2022年に96歳で死去した*5。',
      citations: [
        { num: 1, name: 'International Center of Photography — William Klein', url: 'https://www.icp.org/browse/archive/constituents/william-klein' },
        { num: 2, name: 'Howard Greenberg Gallery — William Klein', url: 'https://www.howardgreenberg.com/artists/william-klein' },
        { num: 3, name: 'i-D — William Klein was 20th century fashion photography&#39;s creative freak', url: 'https://i-d.co/article/william-klein-photography/' },
        { num: 4, name: 'Artforum — William Klein and the Radioactive Fifties', url: 'https://www.artforum.com/features/william-klein-and-the-radioactive-fifties-214042/' },
        { num: 5, name: 'Metropolitan Museum of Art — William Klein', url: 'https://www.metmuseum.org/art/collection/search/266102' }
      ]
    }
  },

  {
    id: 'araki',
    name: 'Nobuyoshi Araki',
    nameJa: '荒木経惟',
    nationality: 'JP',
    flag: '🇯🇵',
    years: '1940–',
    gender: '男性',
    era: '1950',
    movements: ['私写真', '日本写真'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (JA)', url: 'https://ja.wikipedia.org/wiki/%E8%8D%92%E6%9C%A8%E7%B5%8C%E6%83%9F' },
      { label: 'Artscape', url: 'https://artscape.jp/artword/index.php/%E8%8D%92%E6%9C%A8%E7%B5%8C%E6%83%9F' },
    ],
    amazon: '',
    context: {
      text: '荒木経惟は電通の広告写真家として働く傍ら、同社の秘書として働いていた青木陽子（ヨーコ）と1971年7月7日に結婚した。その新婚旅行（柳川・九州）で撮影した写真を私家版写真集『センチメンタルな旅』（1971年）として自費出版したのが、彼の写真家としての出発点となった*1。この写真集はホテルの朝食・窓からの景色・ヨーコとの私的な場面を日常スナップの形式で収録したもので、「私的な最も内密な記憶の公開」という行為そのものをアート実践として提示した*2。荒木は自らの写真スタイルを「私写真」と名付けた。これは日本の「私小説」——一人称の語り手が自身の内面と親密な関係を赤裸々に描く文学形式——から着想した概念であり、「写真家の主観的な生の体験」を芸術の正当な主題として位置づけるものだった*3。当時の写真界は報道（客観・中立）と美術（形式・距離）に二分されており、個人的なスナップは芸術とみなされなかった。荒木がこの境界を問い続けた理由は、最も私的なものこそが最も普遍的であるという確信にあった——自分とヨーコの愛・性・死は誰もが経験する生の本質であり、その記録は個人日記である以前に人間の条件の証言だという認識である*3。「写真は呼吸と同じくらい自然なものだ。写真は生そのものだ」というアラキの言葉はこの確信を端的に示す*3。エロス・死・時間は彼の一貫した主題で、1993年の写真集『エロトス』はギリシア神話のエロス（愛・欲望）とタナトス（死）を題名に重ね、「生の喜びと死の予感が出会い混ざり合う」と述べている*3。当時のプロヴォーク運動（中平卓馬・森山大道ら）の反乱精神と共鳴しながらも、「私は正式に参加できなかったが、反乱の精神は共有した」と語っており、日本の前衛写真の文脈に位置しながら独自の軌道を歩んだ*3。虚実の境界——撮影された親密な場面が「真正の私的瞬間」なのか「演出された構築物」なのか——もアラキ作品が問い続けた核心だった。1992年には猥褻物陳列罪で写真集販売に関わったギャラリー従業員が摘発され、荒木自身も繰り返し検閲と衝突しながら法の輪郭を試し続けた*3。1990年のヨーコの卵巣癌による死は「冬の旅」という続篇を生み、愛・生・喪失という弧を写真集として完結させた*4。ヴェネツィア・ビエンナーレ（1997年）をはじめ欧米の主要美術館で多数の個展が開催され、100冊超の写真集を刊行している*5。「私が写真を撮らなければ、私には何もない」という言葉が示すように、撮影は彼にとって生の記録であると同時に生の実践そのものだった*3。',
      citations: [
        { num: 1, name: 'shashasha — Nobuyoshi Araki: Sentimental Journey', url: 'https://www.shashasha.co/en/book/nobuyoshi-araki-sentimental-journey-1971-2017' },
        { num: 2, name: 'AnOther Magazine — Exposing Nobuyoshi Araki&#39;s Most Sentimental Series', url: 'https://www.anothermag.com/art-photography/8792/exposing-nobuyoshi-arakis-most-sentimental-series' },
        { num: 3, name: 'Duke University Press — Crossing Boundaries: An Interview with Nobuyoshi Araki', url: 'https://read.dukeupress.edu/trans-asia-photography/article/doi/10.1215/215820251_1-2-205/312607/Crossing-Boundaries-An-Interview-with-Nobuyoshi' },
        { num: 4, name: 'Singulart — Sentimental Journey by Nobuyoshi Araki: An Exploration of Love', url: 'https://www.singulart.com/blog/en/2024/06/03/sentimental-journey-by-nobuyoshi-araki/' },
        { num: 5, name: 'p55.art — Who was the Japanese photographer Nobuyoshi Araki?', url: 'https://www.p55.art/en/blogs/p55-magazine/who-was-the-japanese-photographer-nobuyoshi-araki' }
      ]
    }
  },

  {
    id: 'tomatsu',
    name: 'Shomei Tomatsu',
    nameJa: '東松照明',
    nationality: 'JP',
    flag: '🇯🇵',
    years: '1930–2012',
    gender: '男性',
    era: '1950',
    movements: ['日本写真', '社会ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'SFMOMA', url: 'https://www.sfmoma.org/artist/shomei_tomatsu/' },
      { label: 'Wikipedia (JA)', url: 'https://ja.wikipedia.org/wiki/%E6%9D%B1%E6%9D%BE%E7%85%A7%E6%98%8E' },
    ],
    amazon: '',
    context: {
      text: '東松照明は1930年に名古屋で生まれ、戦時中に軍需工場に動員された世代として、終戦と同時にアメリカ軍の占領を直接経験した。占領軍の兵士に対する個人的な親切と、その存在が日本社会に与える暴力性への反感が同時に存在する、「愛憎」の複雑な感情が、その後の生涯のテーマを形成した*1。東松にとって写真の使命は「戦後日本社会の内側からの記録」にあった。戦時中に刷り込まれた国家プロパガンダへの不信から、「世界で信じられるのは、自分の目で実際に見たものだけだ」という確信を持つに至り、外部のジャーナリストや占領軍が提示する「外側からのジャパン像」ではなく、占領・原爆・高度成長の渦中を生きた日本人としての内側の証言を積み重ねることを一貫して選んだ*1。「敗戦後、闇と光が明確に見えるようになり、価値観が180度転換した」というSFMOMAに収録された東松自身の言葉は、この世代的体験が写真行為の根拠になったことを示している*5。1959年に土門拳・奈良原一高らとともに写真家集団「VIVO」を設立し、「主観的ドキュメンタリー」——純粋な記録と表現主義的な印画技法・劇的な角度・象徴的な構成を融合させる手法——を確立した*2。1960年の「占領——チューインガムとチョコレート」シリーズは、日本各地の米軍基地周辺を撮影したもので、アメリカ兵と日本人女性の接触・均質的な日本社会への異人種の出現・抵抗文化の発生など、占領がもたらした「アメリカニゼーション」の諸相を記録した*3。1960年に長崎を初めて訪れ、1945年8月9日の原爆投下後も生き続けた被爆者（ヒバクシャ）を撮影し始めた。1961年にはその成果が土門拳のヒロシマ写真とともに『ヒロシマ・ナガサキ・ドキュメント1961』（ロシア語・英語のみで刊行）に収録された。1966年刊行の写真集『11時02分 NAGASAKI』では、原爆の熱線に溶けたビール瓶・止まった時計・破壊された浦上天主堂の断片など事物の記録と被爆者の肖像が組み合わされた*4。東松の最も有名な一枚とされる「溶けたビール瓶」は、核爆発が物質に刻んだ痕跡を通じて、戦後日本の暴力と変容を可視化した作品として評価されている。若い世代の森山大道・中平卓馬ら「プロヴォーク」グループへの影響が指摘されており、サンフランシスコ近代美術館・シカゴ美術館などで大規模な個展が開催されている*5。',
      citations: [
        { num: 1, name: 'Smithsonian National Museum of Asian Art — Tomatsu Shomei', url: 'https://asia-archive.si.edu/exhibition/tomatsu-shomei/' },
        { num: 2, name: 'Michael Hoppen Gallery — Shomei Tomatsu', url: 'https://www.michaelhoppengallery.com/artists/64-shomei-tomatsu/' },
        { num: 3, name: 'Aperture — Remembering Shomei Tomatsu (1930-2012)', url: 'https://aperture.org/editorial/remembering-shomei-tomatsu-1930-2012/' },
        { num: 4, name: 'shashasha — Shomei Tomatsu', url: 'https://www.shashasha.co/en/artist/shomei-tomatsu' },
        { num: 5, name: 'SFMOMA — Shomei Tomatsu', url: 'https://www.sfmoma.org/artist/Shomei_Tomatsu/' }
      ]
    }
  },

  {
    id: 'winogrand',
    name: 'Garry Winogrand',
    nameJa: 'ゲリー・ウィノグランド',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1928–1984',
    gender: '男性',
    era: '1950',
    movements: ['ストリート写真', 'アメリカ写真', 'ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Garry_Winogrand' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/Garry-Winogrand' },
      { label: 'Fraenkel Gallery', url: 'https://fraenkelgallery.com/artists/garry-winogrand' },
    ],
    amazon: '',
    context: {
      text: 'ガリー・ウィノグランドはニューヨーク・ブロンクス生まれで、1950年代に雑誌のフリーランス写真家としてキャリアを始め、35mmライカカメラを常に携帯して街頭での速写を続けた。その独自のスタイルは「アブストラクト・エクスプレッショニズムに近い、鋭い対角線で構成された動的な構図」と評されている*1。1967年、MoMAの写真部門ディレクター、ジョン・ザルコウスキーが企画した展覧会「ニュー・ドキュメンツ」にダイアン・アーバスとリー・フリードランダーとともに参加し、「彼の世代の中心的な写真家」と位置づけられた*2。ザルコウスキーはこの世代の作品に「スナップショット美学」の概念を定式化した——傾いたフレーム・動体のブレ・一見不安定な構図など、従来の美術写真の規範を逸脱する視覚言語を写真固有の美学として肯定したのである。ウィノグランドの画面についてザルコウスキーは「混沌とした表面の下に、ほぼ無意識に感じ取れる秩序がある——それが作者の視覚的知性の証だ」と評している*5。ウィノグランドの師アレクセイ・ブロドヴィッチは「方法論や技術ではなく直感に頼れ」と説き、この哲学はウィノグランドの撮影姿勢の核となった*6。「写真を撮るのは、世界が写真の中でどう見えるかを確かめるためだ——私には前もって言いたいことなど何もない」という言葉はこの方法論を端的に示す。ウィノグランドは撮影後すぐにフィルムを現像しなかった——「撮影した日の気分が残っていると、その記憶で写真を選んでしまう」という理由から、1〜2年時間を置いてから作業した。1975年刊行の写真集『女たちは美しい』は85点の女性の写真を収録し、フェミニスト批評から性差別的と批判される一方、「1970年代のフェミニズム台頭と性的変容の時代における女性の表現」の記録とする評価もある*3。1975年頃からテキサス・ロサンゼルスへと生活の拠点を移し、撮影スタイルはより暗く複雑なものへと変化した。1984年に56歳でガンにより急死し、現像済みだが未プルーフの6,500本のフィルムと未現像2,500本を含む合計30万点もの未整理写真を遺した*4。この膨大な「未完の仕事」はアリゾナ大学クリエイティブ・フォトグラフィー・センターに収蔵され、1988年のMoMAでの回顧展（ザルコウスキー企画）でその一部が公開された。「私はアメリカの学生だ」という言葉が示すように、彼の写真は変動するアメリカ社会の断面を鋭く切り取り続けた*5。',
      citations: [
        { num: 1, name: 'Phaidon — The Pioneering Street Photography of Garry Winogrand', url: 'https://www.phaidon.com/en-us/blogs/artspace/the-pioneering-photography-of-garry-winogrand' },
        { num: 2, name: 'MoMA — Garry Winogrand, Women are Beautiful', url: 'https://www.moma.org/collection/works/111102' },
        { num: 3, name: 'Denver Art Museum — Garry Winogrand: Women are Beautiful', url: 'https://www.denverartmuseum.org/en/exhibitions/garry-winogrand-women-are-beautiful' },
        { num: 4, name: 'Public Delivery — Garry Winogrand&#39;s Women are Beautiful – 50 years later', url: 'https://publicdelivery.org/garry-winogrand-women-are-beautiful/' },
        { num: 5, name: 'Fraenkel Gallery — Garry Winogrand', url: 'https://fraenkelgallery.com/artists/garry-winogrand' },
        { num: 6, name: 'Britannica — Garry Winogrand', url: 'https://www.britannica.com/biography/Garry-Winogrand' }
      ]
    }
  },

  {
    id: 'friedlander',
    name: 'Lee Friedlander',
    nameJa: 'リー・フリードランダー',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1934–',
    gender: '男性',
    era: '1950',
    movements: ['ストリート写真', 'アメリカ写真', 'ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/calendar/exhibitions/113' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Lee_Friedlander' },
    ],
    amazon: '',
    context: {
      text: 'リー・フリードランダーはワシントン州アバディーン生まれで、1953年からロサンゼルスのアート・センター・スクールで写真を学び、1956年からニューヨークを拠点にエスクァイア・スポーツ・イラストレイテッドなど雑誌の仕事を手がけた。1966年、ネイサン・ライアンズがジョージ・イーストマン・ハウスで企画した展覧会「社会的風景に向けて（Toward a Social Landscape）」にブルース・デイヴィッドソン・ガリー・ウィノグランドらとともに参加した*1。フリードランダー自身が語った「ソーシャルランドスケープ」とは自然の風景の対極——都市・道路・建物・商業空間・自動車という人間が作り上げた環境のことであり、社会改革のための記録ではなく、その環境をそのまま個人的な視点で知ろうとする試みを意味した。1967年のMoMA「ニュー・ドキュメンツ」展（ダイアン・アーバス・ガリー・ウィノグランドとともに）では、キュレーターのジョン・ザルコウスキーが「目的は生活を改革することではなく、それを知ることだ」と評し、フリードランダーをアメリカ写真の新しい世代の代表として決定的に位置づけた*2。彼の特徴的な構成法は、ショーウィンドウのガラス・鏡・窓への反射と透過が重なって空間・光・物体が視覚的な層を形成する点にある。不透明さと透明さが同一画面で共存し、街路標識・電話ボックス・チェーンフェンスといった「ストリート・ファーニチャー」がサブ・フレームとして画面を分割するこの手法を都市の路上に応用することで、アメリカの都市空間が持つ「遮蔽・混乱・偶然」を視覚言語に変換した*3。また窓や鏡への映り込み、あるいは影だけとして自らを画面に組み込む「セルフポートレート」手法は、写真家自身を不可視にすることが常識だった時代へのラディカルな問いかけだった。フリードランダーの画面はウォーカー・エヴァンズとユージン・アジェの明晰さを継承しながら、ポップ・アートの皮肉とユーモアを組み合わせたと評されている*4。2005年にMoMAで大規模な回顧展が開催され、写真・セルフポートレート・ヌード・風景・都市の各シリーズが網羅された。シカゴ美術館・メトロポリタン美術館・国立美術館・ホイットニー美術館など主要機関が作品を収蔵しており、ロバート・フランク以降のアメリカ写真を定義した写真家の一人として位置づけられている*5。',
      citations: [
        { num: 1, name: 'Common Edge — The Social Landscapes of Lee Friedlander', url: 'https://commonedge.org/the-social-landscapes-of-lee-friedlander/' },
        { num: 2, name: 'International Center of Photography — Lee Friedlander', url: 'https://www.icp.org/browse/archive/constituents/lee-friedlander' },
        { num: 3, name: 'The Art Story — Lee Friedlander', url: 'https://www.theartstory.org/artist/friedlander-lee/' },
        { num: 4, name: 'B&W Magazine — The Social Landscapes of Lee Friedlander', url: 'https://www.bandwmag.com/articles/the-social-landscapes-of-lee-friedlander' },
        { num: 5, name: 'Whitney Museum of American Art — Lee Friedlander', url: 'https://whitney.org/artists/465' }
      ]
    }
  },

  /* ─────────────────────────────────────────
     1970–1980s
     ───────────────────────────────────────── */

  {
    id: 'arbus',
    name: 'Diane Arbus',
    nameJa: 'ダイアン・アーバス',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1923–1971',
    gender: '女性',
    era: '1970',
    movements: ['ドキュメンタリー', 'ポートレート', '社会ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'Aperture', url: 'https://aperture.org/books/diane-arbus-an-aperture-monograph/' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Diane_Arbus' },
    ],
    amazon: '',
    context: {
      text: 'ダイアン・アーバスは1923年ニューヨーク生まれ。裕福なユダヤ系家庭に育ち、18歳で写真家アラン・アーバスと結婚して1950年代は夫婦でヴォーグ・ハーパーズ・バザーのファッション写真を担当した。しかし安定した商業写真のキャリアに閉塞感を覚えた彼女は1950年代後半にリゼット・モデルに師事し、表現の方向を根本から転換した。モデルの指導のもと、障害者・小人・双子・ヌーディスト・横断着衣者など社会の周縁に生きる人々へカメラを向けるようになった*1。彼女はこうした被写体を「フリークス（奇人）」と呼んだが、それは蔑称ではなく「すでに人生の試練を乗り越えた貴族たち」という意味合いであり、長時間被写体と交流し信頼関係を構築してから撮影するという手法は「写真家と被写体の間の適切な距離」という慣習的規範を根本から問い直すものだった。ニューヨークのダウンタウンやサーカス、精神病院などあらゆる場所に足を運び、被写体を正面から捉える独自のスタイルを確立した。1963年・1966年とグッゲンハイム・フェローシップを連続受賞し精力的に制作を続けた。1967年2月28日にMoMAで開幕したジョン・ザーカウスキー企画の展覧会「ニュー・ドキュメンツ」では、リー・フリードランダー・ゲリー・ウィノグランドとともに、ドキュメンタリー写真を「より個人的な目的に向け直した」写真家として位置づけられた*2。この展覧会は当初目録すら制作されなかったが、50周年を機に刊行された記念書籍が出展94点を初めて完全収録した。同年ニュージャージー州ロゼルで撮影した「双子（ニュージャージー州ロゼル、1967年）」は、同じ顔でありながら微妙に異なる表情を捉えたポートレートで、シカゴ美術館など複数の主要コレクションに収蔵される代表作となった*3。彼女のポートレートが持つ親密さと暴露性は批評家を二分したが、1970年代以降その作品は写真史の重要な転換点として広く認められている。ICPは彼女を「写真の語り方を変えた人物」として記録している*4。1971年7月、アーバスは48歳で死去した。翌1972年、ヴェネツィア・ビエンナーレに作品が展示された最初のアメリカ人写真家となった。同年アパーチャー財団がマービン・イズラエルとドゥーン・アーバス編集による遺作集を刊行し、「その功績の幅と力を一般に初めて示した」モノグラフとして5言語版を経て現在も版を重ね続けている*5。',
      citations: [
        { num: 1, name: 'The Art Story — Diane Arbus', url: 'https://www.theartstory.org/artist/arbus-diane/' },
        { num: 2, name: 'MoMA — New Documents, 1967', url: 'https://www.moma.org/calendar/exhibitions/3487' },
        { num: 3, name: 'Art Institute of Chicago — Identical Twins, Roselle, N.J.', url: 'https://www.artic.edu/artworks/67958/identical-twins-roselle-n-j' },
        { num: 4, name: 'ICP — Diane Arbus', url: 'https://www.icp.org/browse/archive/constituents/diane-arbus' },
        { num: 5, name: 'Aperture — Diane Arbus: An Aperture Monograph', url: 'https://aperture.org/books/diane-arbus-an-aperture-monograph/' }
      ]
    }
  },

  {
    id: 'moriyama',
    name: 'Daido Moriyama',
    nameJa: '森山大道',
    nationality: 'JP',
    flag: '🇯🇵',
    years: '1938–',
    gender: '男性',
    era: '1970',
    movements: ['プロヴォーク', '日本写真', 'ストリート写真'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (JA)', url: 'https://ja.wikipedia.org/wiki/%E6%A3%AE%E5%B1%B1%E5%A4%A7%E9%81%93' },
      { label: 'Artscape', url: 'https://artscape.jp/artword/index.php/%E6%A3%AE%E5%B1%B1%E5%A4%A7%E9%81%93' },
    ],
    amazon: '',
    context: {
      text: '森山大道は1938年大阪府池田市生まれ。岩宮武二・細江英公のアシスタントを経て1961年に独立し、1968年創刊の写真誌「プロヴォーク」の第2号から参加した。竹内泰宏・中平卓馬・多木浩二・岡田隆彦らが「思想のためのちょうはつてき資料」を副題に創刊した同誌はわずか3号で廃刊となったが、当時の日本写真表現を根本から変えた*1。森山がプロヴォークで実践したのは「アレ・ブレ・ボケ」——粗い粒子・手ブレ・ピントの外れた被写体——という従来の「きれいな写真」の美学を否定するスタイルだった。高コントラストの黒白で都市の断片を捉えたこの手法は、高度成長期日本の解体と混乱の感覚を直接体現するものだった*2。1972年には写真集「写真よさようなら」を刊行し、中平卓馬との対話とともに写真というメディアそのものを根本的に解体しようとする姿勢を示した。この写真集はのちにテート・ギャラリーのコレクションに収蔵されるほど評価が高まっている*3。その後も1968年以来150冊以上の写真集を発表し続け、作品のテーマと形式を絶えず刷新してきた。2012〜13年にテート・モダンで開催されたウィリアム・クラインとの二人展は「両者の作品の関係性を初めて本格的に検証した展覧会」と評された*2。2019年にはハッセルブラッド財団国際写真賞を受賞し、選考委員長ポール・ロスは「史上最も重要で影響力ある写真家の一人」と評した*4。MoMAも森山の作品を恒久コレクションとして収蔵しており*5、そのアレ・ブレ・ボケの美学はウォルフガング・ティルマンスら後続世代の写真家に多大な影響を与え、日本の写真表現の国際的評価を確立する礎となった。ウィリアム・クラインやウォーカー・エヴァンズの影響を受けつつ、森山は東京の街頭を手持ちカメラで歩きながら高速でシャッターを切る撮影スタイルを確立した。プロヴォーク時代の作品は1968〜69年の学生運動が高揚した時代と軌を一にしており、写真が社会の矛盾と向き合う武器となりうるという時代感覚を色濃く反映している。1968年の写真集「日本劇場写真帖」を皮切りに、「新宿」（1968年）「氷」（1968年）「写真よさようなら」（1972年）など次々と写真集を発表し、形式と内容を絶えず更新し続けた。晩年に至るまでフィルムプリントから携帯電話撮影まで素材を問わず実験を続け、「写真とは何か」を問い直す姿勢を貫いている。',
      citations: [
        { num: 1, name: 'MoMA — For the Sake of Thought: Provoke, 1968–1970', url: 'https://www.moma.org/explore/inside_out/2013/01/25/for-the-sake-of-thought-provoke-1968-1970/' },
        { num: 2, name: 'Tate — Daido Moriyama artist page', url: 'https://www.tate.org.uk/art/artists/daido-moriyama-11595' },
        { num: 3, name: 'Tate — Farewell Photography, 写真よさようなら', url: 'https://www.tate.org.uk/art/artworks/moriyama-farewell-photography-p79977' },
        { num: 4, name: 'Hasselblad Foundation — Hasselblad Award Winner 2019', url: 'https://www.hasselbladfoundation.org/en/hasselblad-award-winner-2019/' },
        { num: 5, name: 'MoMA — Daido Moriyama artist page', url: 'https://www.moma.org/artists/4099' }
      ]
    }
  },

  {
    id: 'sherman',
    name: 'Cindy Sherman',
    nameJa: 'シンディ・シャーマン',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1954–',
    gender: '女性',
    era: '1970',
    movements: ['ピクチャーズ世代', 'コンセプチュアル', 'フェミニズム写真'],
    thumbnail: '',
    links: [
      { label: 'MoMA', url: 'https://www.moma.org/artists/5376' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Cindy_Sherman' },
    ],
    amazon: '',
    context: {
      text: 'シンディ・シャーマンは1954年ニュージャージー生まれ。1977年から1980年にかけて、1950〜60年代のハリウッド映画・フィルム・ノワール・ヨーロッパ芸術映画を模倣したかのような69点の黒白写真シリーズ「アンタイトルド・フィルム・スティルズ」を制作した。シャーマン自身が監督・モデル・スタイリスト・撮影のすべてを一人でこなし、イングニュー・働く女性・ヴァンプ・孤独な主婦などの典型的な女性像を演じた*1。スタジオ外で撮影した唯一のシリーズであり、各写真は映画のスチール写真のように見えながら実際には存在しない映画の一場面を示すという虚構の重層構造を持つ。MoMAは1995年に69点の全シリーズを収蔵し*1、翌1996〜97年に「シンディ・シャーマン：ザ・コンプリート・アンタイトルド・フィルム・スティルズ」展を開催した*2。このシリーズは1970年代後半のニューヨークに登場した「ピクチャーズ・ジェネレーション」の中核的作品と位置づけられる。リチャード・プリンス・シェリー・レヴァイン・ロバート・ロンゴらとともに、シャーマンはマス・メディアの既成イメージを流用・再構築することで「大量に流通するイメージの中に内在する権力構造」を可視化しようとした*3。フェミニズム批評の観点からは、自己演出によって女性が視線の客体として消費される構造そのものを解体する実践として論じられてきた。1981年の「アンタイトルド #96」（アートフォーラム誌から依頼されたセンターフォールズシリーズより）は2011年のクリスティーズオークションで389万ドルの当時写真作品最高額を記録した*4。MoMAは現在42点の作品を収蔵しており*5、シャーマンは「ポストモダン写真の揺るぎない礎石」と評価されている。アンタイトルド・フィルム・スティルズ以降も、シャーマンは「センターフォールズ」（1981年）・「ヒストリー・ポートレーツ」（1988〜90年）・「ディザスター」（1986〜89年）・「セックス・ピクチャーズ」（1992年）など多彩なシリーズを発表し、一貫して「誰かを演じる自分」を主題とし続けた。自分自身を使いながら「自己」を不在にするというパラドックスに満ちたその戦略は、ローラン・バルトやジャック・ラカンの理論との親和性からアカデミックな文脈でも広く論じられた。2012年にはMoMAで大規模な回顧展が開催され、約170点が展示された。',
      citations: [
        { num: 1, name: 'MoMA — Cindy Sherman artist page', url: 'https://www.moma.org/collection/artists/5392' },
        { num: 2, name: 'MoMA — Cindy Sherman: The Complete Untitled Film Stills, 1997', url: 'https://www.moma.org/calendar/exhibitions/253' },
        { num: 3, name: 'ICP — Pictures Generation, 1974–1984', url: 'https://www.icp.org/content/pictures-generation-1974-1984' },
        { num: 4, name: 'Popular Photography — Cindy Sherman Print Sells For $3.9 Million At Auction', url: 'https://www.popphoto.com/news/2011/05/cindy-sherman-print-sells-39-million-auction-highest-ever-photograp/' },
        { num: 5, name: 'The Art Story — Cindy Sherman', url: 'https://www.theartstory.org/artist/sherman-cindy/' }
      ]
    }
  },

  {
    id: 'mapplethorpe',
    name: 'Robert Mapplethorpe',
    nameJa: 'ロバート・メイプルソープ',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1946–1989',
    gender: '男性',
    era: '1970',
    movements: ['コンセプチュアル', 'ポートレート'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Robert_Mapplethorpe' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/Robert-Mapplethorpe' },
    ],
    amazon: '',
    context: {
      text: 'ロバート・マッピルソープは1946年ニューヨーク・フラッシング生まれ。プラット・インスティテュートで美術を学んだのち、1970年にポラロイドカメラで写真を撮り始め、独学でスタジオ写真へと発展させた。1978年にはX・Y・Zの3部作ポートフォリオを制作した。Xポートフォリオはニューヨークのゲイ・S&Mシーンを被写体とした13点、Yポートフォリオは花の静物、Zポートフォリオは黒人男性のポートレートから構成される*1。アンディ・ウォーホル・パティ・スミス・トルーマン・カポーティ・ルイーズ・ブルジョワ・フィリップ・グラスらのポートレートでも知られ、1988年にはホイットニー美術館で最初の大規模回顧展が開催された。1989年には、フィラデルフィアを皮切りに始まった巡回展「ザ・パーフェクト・モーメント」をめぐって大きな論争が起きた*2。ワシントンDCのコーコラン・ギャラリーが連邦議会との衝突を避けるため7月1日予定だった開幕を直前でキャンセルし、ジェシー・ヘルムズ上院議員はNEA（全米芸術基金）が「わいせつ」な芸術に資金提供することを禁じる法案を提出した*3。翌1990年、シンシナティのコンテンポラリー・アーツ・センター（CAC）と館長デニス・バリーが7点の写真に対して4件の刑事起訴を受けた。「美術館が展示作品に関する刑事訴追を受けた初の事例」として注目された裁判は、最終的に無罪評決となった*3。1986年にAIDSの診断を受けたマッピルソープは創作を加速させ、1989年3月9日、42歳で死去した。生前に設立したロバート・マッピルソープ財団は写真芸術の支援とAIDS研究への資金提供を継続している*1。マッピルソープの写真は古典絵画の均衡と形式美の原理を写真に適用したような構図を特徴とする。花のシリーズでは蓮・カラー・チューリップなどを彫刻的な精度で撮影し、性的な被写体と同じ美的秩序で提示することで鑑賞者の倫理的判断を宙吊りにした。1972年に出会ったパティ・スミスとのパートナーシップは彼の芸術的成長を支え、スミスは「彼は美の追求者だった」と述べている。1988年のホイットニー回顧展には延べ10万人以上が来場し、商業的・批評的双方で高い評価を受けた。没後もロバート・マッピルソープ財団はAIDS研究への資金提供と写真芸術の支援を続けており、その遺産は現在に至るまで活発に維持されている*5。',
      citations: [
        { num: 1, name: 'Mapplethorpe Foundation — Biography', url: 'https://www.mapplethorpe.org/biography' },
        { num: 2, name: 'Mapplethorpe Foundation — The Perfect Moment', url: 'https://www.mapplethorpe.org/selected-publications/the-perfect-moment' },
        { num: 3, name: 'Smithsonian Magazine — When Art Fought the Law and the Art Won', url: 'https://www.smithsonianmag.com/history/when-art-fought-law-and-art-won-180956810/' },
        { num: 4, name: 'Smithsonian Magazine — How a Museum Cancelling a Controversial Mapplethorpe Exhibition Changed My Life', url: 'https://www.smithsonianmag.com/arts-culture/how-museum-cancelling-controversial-mapplethorpe-exhibition-changed-my-life-180959311/' },
        { num: 5, name: 'ICP — Robert Mapplethorpe', url: 'https://www.icp.org/browse/archive/constituents/robert-mapplethorpe' }
      ]
    }
  },

  {
    id: 'kruger',
    name: 'Barbara Kruger',
    nameJa: 'バーバラ・クルーガー',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1945–',
    gender: '女性',
    era: '1970',
    movements: ['ピクチャーズ世代', 'コンセプチュアル', 'フェミニズム写真'],
    thumbnail: '',
    links: [
      { label: 'The Broad', url: 'https://www.thebroad.org/art/barbara-kruger/untitled-your-body-battleground' },
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Barbara_Kruger' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/Barbara-Kruger' },
    ],
    amazon: '',
    context: {
      text: 'バーバラ・クルーガーは1945年ニュージャージー州ニューアーク生まれ。パーソンズ美術大学でダイアン・アーバスとマービン・イズラエルに学んだのち、コンデ・ナスト社の雑誌「マドモアゼル」でアートディレクターを務めた。1970年代後半に自身で撮影した写真を使うことをやめ、報道・広告・記録写真などの「見つけた写真」をベースに制作するようになった。白黒の既成写真に赤地白抜きの「フーツラ・ボールド・オブリーク」体（またはヘルベチカ・ウルトラ・コンデンスド体）で断定的な文句を重ねるスタイルは、広告や雑誌レイアウトの視覚言語を逆手に取り、権力・アイデンティティ・消費主義への批判を表現するものとなった*1。代表作「アンタイトルド（私は買い物をする、ゆえに私は存在する）」（1987年）はレーガノミクス時代の消費主義を皮肉に批判した作品であり*2、「アンタイトルド（あなたの身体は戦場だ）」（1989年）は中絶権を求めるワシントンDCの女性行進のために制作された*2。「ピクチャーズ・ジェネレーション」の主要メンバーとしてシャーマン・プリンスらと並び称され*3、2022〜23年にはMoMAで大規模な個展「あなたのことを考えている。私のことを。あなたのことを。」が開催された*4。赤地白抜きのメッセージは展示空間そのものへと拡張され、ギャラリーの床・壁・天井を一体として覆うインスタレーションへと発展した。ニューヨークのメトロポリタン交通局のバスや電車の車内広告枠、ニューヨーク・タイムズ紙の全面広告など公共空間への進出も積極的に行った。グッゲンハイム・フェローシップ（1983年）受賞。クルーガーの実践は写真・テキスト・空間を統合したアプローチとして後続の世代の視覚芸術家に広く影響を与え、パブリックアートのあり方を拡張した*5。',
      citations: [
        { num: 1, name: 'Whitney Museum — Barbara Kruger artist page', url: 'https://whitney.org/artists/2635' },
        { num: 2, name: 'The Art Story — Barbara Kruger', url: 'https://www.theartstory.org/artist/kruger-barbara/' },
        { num: 3, name: 'ICP — Pictures Generation, 1974–1984', url: 'https://www.icp.org/content/pictures-generation-1974-1984' },
        { num: 4, name: 'MoMA — Barbara Kruger: Thinking of You. I Mean Me. I Mean You.', url: 'https://www.moma.org/calendar/exhibitions/5394' },
        { num: 5, name: 'Tate — Barbara Kruger artist page', url: 'https://www.tate.org.uk/art/artists/barbara-kruger-1443' }
      ]
    }
  },

  {
    id: 'eggleston',
    name: 'William Eggleston',
    nameJa: 'ウィリアム・エグルストン',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1939–',
    gender: '男性',
    era: '1970',
    movements: ['カラー写真', 'アメリカ写真', 'ドキュメンタリー'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/William_Eggleston' },
      { label: 'Britannica', url: 'https://www.britannica.com/biography/William-Eggleston' },
    ],
    amazon: '',
    context: {
      text: 'ウィリアム・エグルストンは1939年テネシー州メンフィス生まれ。1960年代から35mmのカラーフィルムで撮影を始め、1976年にMoMAでジョン・ザーカウスキーの企画により「ウィリアム・エグルストン・ガイド」展を開催した。これは「MoMAが開催した初のカラー写真単独個展であり、初のカラー写真出版物」として記録される歴史的展覧会だった*1。ガイドには1969〜71年に撮影された375点から選定された48点が収められた。ショッピングセンター・ガソリンスタンド・郊外の民家・赤信号・電球が下がる天井など、誰もが見過ごすような南部の日常の断片を捉えたエグルストンのスタイルは「民主的なカメラ」と呼ばれた*2。「被写体のヒエラルキーを認めない」というこの姿勢は、写真においてロケーションや題材の「重要性」が問われてきた従来の価値観を根本から覆した。技法面では商業印刷のダイ・トランスファー・プリントを初めて芸術表現に転用し、艶やかに飽和した発色で光と色の強度を最大化した*3。1974年グッゲンハイム・フェローシップ受賞、1998年ハッセルブラッド財団国際写真賞受賞*4。2008〜09年にはホイットニー美術館で「ウィリアム・エグルストン：デモクラティック・カメラ、写真とビデオ1961〜2008」と題したアメリカ初の大規模回顧展が開催された*2。そのバナールなものを「とても大げさに」写し取るスタイルはナン・ゴールディン・ウォルフガング・ティルマンス、映画監督ガス・ヴァン・サント・ソフィア・コッポラらに影響を与え、カラー写真を写真史の中心に据えることに貢献した*3。MoMAは複数の作品を恒久コレクションとして収蔵している*5。1976年の展覧会は批評家の反応を二分し、批判的な評者はショッピングセンターや電球といった平凡な題材を大型美術館で展示する行為を「年間最悪の展覧会」と酷評した。しかしザーカウスキーは「カラー写真はスナップショットかファッション写真かポルノグラフィーにしか使われていなかった。エグルストンはそれをファインアートにした」と擁護した。その評価は時代とともに一転し、1977年刊行の写真集「ウィリアム・エグルストン・ガイド」はMoMA史上最も重要な写真出版物の一つと位置づけられるようになった。フィルム監督ガス・ヴァン・サントは「彼の写真は映画的なフレームの感覚を教えてくれた」と述べており、その影響は写真の枠を超えている*2。',
      citations: [
        { num: 1, name: 'MoMA — William Eggleston&#39;s Guide (1976 exhibition)', url: 'https://store.moma.org/products/william-egglestons-guide-hardcover-3' },
        { num: 2, name: 'Whitney Museum — William Eggleston: Democratic Camera', url: 'https://whitney.org/exhibitions/william-eggleston' },
        { num: 3, name: 'Aperture — The Emotional Saturation of William Eggleston&#39;s Last Dyes', url: 'https://aperture.org/editorial/the-emotional-saturation-of-william-egglestons-last-dyes/' },
        { num: 4, name: 'Hasselblad Foundation — William Eggleston', url: 'https://www.hasselbladfoundation.org/en/portfolio_page/william-eggleston/' },
        { num: 5, name: 'MoMA — William Eggleston artist page', url: 'https://www.moma.org/artists/1690' }
      ]
    }
  },

  /* ─────────────────────────────────────────
     1980s
     ───────────────────────────────────────── */
  {
    id: 'goldin',
    name: 'Nan Goldin',
    nameJa: 'ナン・ゴールディン',
    nationality: 'US',
    flag: '🇺🇸',
    years: '1953–',
    era: '1980',
    movements: ['ドキュメンタリー', 'プライベート写真', 'LGBTQ+'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Nan_Goldin' },
      { label: 'Artnet — Nan Goldin', url: 'https://www.artnet.com/artists/nan-goldin/' },
    ],
    amazon: '',
    context: {
      text: '1953年にワシントンDCで生まれたゴールディンは、11歳で姉バーバラを自殺で失った経験から「写真は愛する人を失う前に記録し続けることができる」という確信を抱き、16歳でカメラを手にした*1。1970年代末にニューヨークへ移り、ボウエリー周辺のゲイ・トランスジェンダー・セックスワーカーのコミュニティに住み込みながら日記代わりに撮影を重ね、積み重ねた690枚超のスライドをバーや映画館でルー・リードやヴェルヴェット・アンダーグラウンドの音楽とともに上映し続けた*2。この記録は1986年にアパーチャー財団から写真集『性的依存のバラッド』として刊行され、アルル国際写真フェスティバルのコダック写真集賞を受賞した*2。「私は写真を記憶の代わりに使う。記憶は失われるが写真は残る」というゴールディン自身の言葉が示すように、彼女の方法論は外部の観察者ではなくコミュニティ内側の当事者が「見せることを選ぶ」という権力関係の逆転を体現しており、同時代の報道写真が保った観察者的距離とは根本的に異なった*1。カメラは彼女にとってコミュニティのメンバーシップ証明であり、被写体との関係性の中から生まれた写真群は、後のSNS時代のセルフドキュメンタリー文化に先行するものとして再評価されている*2。1980年代に猛威を振るったエイズ禍は彼女の「選んだ家族」を次々と奪い、スライドショーは生の記録から悼みの場へと変貌した——バラッドに登場する多くの人物が1990年代初頭までに逝去している*3。1985年のホイットニー・ビエンナーレで美術界に広く知られ、1996年のホイットニー美術館回顧展で国際的評価を確立した*4。作品はMoMA・グッゲンハイム・テートが収蔵し、2007年にはハッセルブラッド賞を受賞した*5。2017年には自身のオキシコンチン依存症の経験から処方薬乱用問題への抗議団体P.A.I.N.（処方薬乱用介入委員会）を結成し、サックラー家の資金を受けていたメトロポリタン・グッゲンハイム・テート・ルーヴルへの抗議を主導した*3。世界の主要美術館が寄附金の返還とサックラーの冠名撤去に応じる事態となり、写真家が美術機関の資金構造そのものを変えた事例として記録されている*1。私的証言を社会変革の道具へと転化させた実践は、2022年にローラ・ポイトラス監督がドキュメンタリー映画化（ヴェネツィア映画祭金獅子賞）して広く知られた*1。',
      citations: [
        { num: 1, name: 'Wikipedia — Nan Goldin', url: 'https://en.wikipedia.org/wiki/Nan_Goldin' },
        { num: 2, name: 'Aperture Foundation — The Ballad of Sexual Dependency', url: 'https://aperture.org/books/the-ballad-of-sexual-dependency/' },
        { num: 3, name: 'The Guardian — Nan Goldin and the opioid crisis', url: 'https://www.theguardian.com/artanddesign/2019/jan/25/nan-goldin-photographer-opioid-crisis-sackler-family' },
        { num: 4, name: 'Whitney Museum — Nan Goldin', url: 'https://whitney.org/artists/3451' },
        { num: 5, name: 'Hasselblad Foundation — Nan Goldin', url: 'https://hasselbladfoundation.org/wp/laureates/nan-goldin/' }
      ]
    }
  },

  {
    id: 'wall',
    name: 'Jeff Wall',
    nameJa: 'ジェフ・ウォール',
    nationality: 'CA',
    flag: '🇨🇦',
    years: '1946–',
    era: '1980',
    movements: ['シネマトグラフィック写真', 'ステージド写真', 'コンセプチュアルアート'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Jeff_Wall' },
      { label: 'Tate — Jeff Wall', url: 'https://www.tate.org.uk/art/artists/jeff-wall-2475' },
    ],
    amazon: '',
    context: {
      text: '1946年バンクーバー生まれのウォールは、ブリティッシュ・コロンビア大学で修士号を取得した後、ロンドンのコートールド美術研究所でT.J.クラークのもとマネとボードレールの近代絵画論を研究し、〙19世紀の絵画が担った都市的現実の記録という機能を写真でいかに更新できるか〝という問いを抱いて1970年代末に写真に転じた*1。ウォールが開発したのは映画のセットのように場所と人物を設定してから撮影する「シネマトグラフィック・アプローチ」で、バックライト透過式ライトボックスに大判プリントを収めた作品はギャラリー壁面をスクリーンのように占有する——このライトボックス形式は街頭広告の看板からヒントを得たとされる*2。1978年の「破壊された部屋」はドラクロワ「サルダナパールの死」（1827年）を参照した最初の大型ライトボックス作品であり、絵画史の文脈を写真に持ち込む手法の出発点となった*1。1993年の「突然の一陣の風（葛飾北斎に倣って）」は北斎「富嶽三十六景・駿州江尻」の構図を現代カナダの工業地帯に移し替えた作品で、100枚超のカットを5か月かけてデジタル合成して完成させ、テート・モダンが収蔵している*3。演出と記録という写真の本質論争を「映画的写真」という概念で無効化し、写真を絵画史と同等の解釈的深さを持つ芸術形式として位置づけた功績は、1990年代以降のコンテンポラリー写真のコレクター市場拡大と美術館への統合に決定的に寄与した*1。2002年にハッセルブラッド賞を受賞し、2005〜06年テート・モダンおよび2007年MoMAで大規模個展が開催された*4。作品はカナダ国立美術館・バンクーバー美術館をはじめ、MoMA・テート・ポンピドゥーセンターなど世界の主要美術館に収蔵されている*4。',
      citations: [
        { num: 1, name: 'Wikipedia — Jeff Wall', url: 'https://en.wikipedia.org/wiki/Jeff_Wall' },
        { num: 2, name: 'Tate — Jeff Wall', url: 'https://www.tate.org.uk/art/artists/jeff-wall-2476' },
        { num: 3, name: 'Tate — A Sudden Gust of Wind (after Hokusai)', url: 'https://www.tate.org.uk/art/artworks/wall-a-sudden-gust-of-wind-after-hokusai-p77872' },
        { num: 4, name: 'Hasselblad Foundation — Jeff Wall', url: 'https://hasselbladfoundation.org/wp/laureates/jeff-wall/' }
      ]
    }
  },

  {
    id: 'gursky',
    name: 'Andreas Gursky',
    nameJa: 'アンドレアス・グルスキー',
    nationality: 'DE',
    flag: '🇩🇪',
    years: '1955–',
    era: '1980',
    movements: ['デュッセルドルフ派', '大判カラー写真', 'コンセプチュアルアート'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Andreas_Gursky' },
      { label: 'Tate — Andreas Gursky', url: 'https://www.tate.org.uk/art/artists/andreas-gursky-2508' },
    ],
    amazon: '',
    context: {
      text: '1955年ライプツィヒ生まれのグルスキーは、写真家の父・祖父のもとで育ち、フォルクヴァング芸術大学でオットー・シュタイネルトに学んだ後、デュッセルドルフ芸術アカデミーでベルント・ベッヒャーに師事した*1。師の「タイポロジー的記録」という方法論を継承しながら、対象を資本主義のグローバルな空間——証券取引所・物流倉庫・スタジアム——へと転じ、高所から大判カメラで撮影した複数カットをデジタル合成することで「人間の目では捉えられない全体像」を構築する手法を確立した*2。1999年の「ライン川（ライン IIシリーズ）」は河川両岸の堤防を幾何学的に整理した極度に抽象化された横断面で、2011年にクリスティーズのオークションで約433万ドルで落札されて当時の写真作品史上最高額を記録した*1。グルスキーの大型プリント（通常150×300センチ超）が示す「無数の反復に溶け込む個人」という構図は、グローバル化した経済システムの均質性と人間の無力さを視覚化するものとして批評家から繰り返し引用されてきた*3。ベッヒャーの弟子仲間であるトーマス・シュトゥルート・トーマス・ルフらとともに「デュッセルドルフ派」と呼ばれ、2001年のMoMA個展をはじめ主要美術館での展覧会を重ね、MoMA・テート・グッゲンハイムが作品を収蔵する*1。デュッセルドルフ芸術アカデミーの教授を長年務め、ドイツ写真研究所の設立にも関与した*2。1999年の「99セント」はアメリカのスーパーマーケットの棚を高密度に捉えた作品で、消費社会の過剰さを「ライン川」と並ぶ代表作として広く知られる*2。写真の分野を超えてファインアートとしての写真市場の価値を飛躍的に高めた先導者として、現代フォトグラフィー・コレクター市場の形成に決定的な役割を果たした*3。',
      citations: [
        { num: 1, name: 'Wikipedia — Andreas Gursky', url: 'https://en.wikipedia.org/wiki/Andreas_Gursky' },
        { num: 2, name: 'Tate — Andreas Gursky', url: 'https://www.tate.org.uk/art/artists/andreas-gursky-2826' },
        { num: 3, name: 'Guggenheim — Andreas Gursky', url: 'https://www.guggenheim.org/artwork/artist/andreas-gursky' }
      ]
    }
  },

  {
    id: 'salgado',
    name: 'Sebastião Salgado',
    nameJa: 'セバスチャン・サルガド',
    nationality: 'BR',
    flag: '🇧🇷',
    years: '1944–',
    era: '1980',
    movements: ['ドキュメンタリー', '社会的写真', '環境写真'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Sebasti%C3%A3o_Salgado' },
      { label: 'Britannica — Sebastião Salgado', url: 'https://www.britannica.com/biography/Sebastiao-Salgado' },
    ],
    amazon: '',
    context: {
      text: '1944年ブラジル・ミナスジェライス州生まれのサルガドは、経済学の博士課程修了後に世界銀行のエコノミストとして赴任したアフリカで写真と出会い、「数字やレポートでは伝わらない人間の苦しみを写真で見せることができる」という確信から1973年にキャリアを転換した*1。ガンマ・シグマを経てマグナム・フォトスに加盟し（1979〜94年）、世界各地の労働現場を取材した。ブラジルのセラ・ペラーダ金鉱山（最盛期に採掘者5万人超）を1986〜89年に取材した写真は工業化以前の人力採掘を地獄絵的スケールで記録し、1993年刊行の写真集『ワーカーズ』（26か国の労働現場を収録）のランドマーク的イメージとなった*2。1994年のルワンダ虐殺取材で難民と死体を撮り続けた経験からPTSDを発症し、帰国後は「私の身体が腐っていくような感覚だった」と語るほど深刻な状態に陥り、しばらく写真を撮れなかった*1。回復の契機となったのは妻レリアとともに故郷農場の荒廃した土地に「インスティトゥート・テラ」を設立し、200万本以上の植樹で熱帯雨林を再生したことで、「写真を離れて自然を回復させることで自分も回復した」と述べている*3。この経験は2013年の写真集『ジェネシス』——手つかずの自然と先住民をモノクロで記録した集大成——への道を開いた*2。サルガドの高コントラストのモノクロ写真が持つ美しさは、「苦しみを美化している」という批評と「美によってのみ人々は直視できる」という擁護の両方を生み出し、ドキュメンタリー写真の倫理論争の焦点に置かれ続けてきた*4。1989年ハッセルブラッド賞・1998年プリンシパル・デ・アストゥリアス芸術賞を受賞し、テート・モダン・グランパレなど世界の主要美術館で大規模回顧展を開催した。2025年5月に81歳で逝去した*1。エコノミストとしての訓練がサルガドに「個人の苦しみをシステムと構造の文脈で捉える」視点をもたらしており、1995〜99年に取材した写真集『移民』（2000年刊）では難民・移住労働者・都市移住者の人口移動をグローバルな視点から描出した*1。スーザン・ソンタグは著書『他者の苦痛へのまなざし』（2003年）でサルガドの写真を具体的に論じ、「美的快楽が苦しみへの共感を麻痺させる」と批判した——これはドキュメンタリー写真史上最も著名な倫理論争のひとつとなった*4。マグナムを離れた後はパリに自身のエージェンシー「アマゾナス・イメージ」を設立し、写真の権利を自ら管理した*2。',
      citations: [
        { num: 1, name: 'Wikipedia — Sebastião Salgado', url: 'https://en.wikipedia.org/wiki/Sebasti%C3%A3o_Salgado' },
        { num: 2, name: 'Magnum Photos — Sebastião Salgado', url: 'https://www.magnumphotos.com/photographer/sebastiao-salgado/' },
        { num: 3, name: 'Instituto Terra', url: 'https://www.institutoterra.org/' },
        { num: 4, name: 'The Guardian — Sebastião Salgado', url: 'https://www.theguardian.com/artanddesign/sebastiao-salgado' }
      ]
    }
  },

  {
    id: 'parr',
    name: 'Martin Parr',
    nameJa: 'マーティン・パー',
    nationality: 'GB',
    flag: '🇬🇧',
    years: '1952–',
    era: '1980',
    movements: ['ドキュメンタリー', 'ニューカラー', 'イギリス写真'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Martin_Parr' },
      { label: 'Martin Parr Foundation', url: 'https://www.martinparr.com/' },
    ],
    amazon: '',
    context: {
      text: '1952年イングランド・サリー州生まれのパーは、マンチェスター工科大学で写真を学んだ後、北イングランドの衰退するコミュニティを撮り続け、1983〜85年の夏にマージーサイドの労働者階級が集うシーサイドリゾート・ニュー・ブライトンを取材した*1。電子フラッシュ・近接・飽和色彩によって記録した写真集『ラスト・リゾート』（1986年刊）は、サッチャー政権下の産業空洞化と格差の中で「格安リゾートに喜ぶしかない人々」を愛情と皮肉の入り混じった目線で描き、英国ドキュメンタリー写真の文法を一変させた*2。パーが飽和色と過剰な接近を選んだのは悲劇的記録の文法を外すためで、「俗悪さを笑いながら愛す」という英国的ユーモアの視点を成立させた*2。1994年のマグナム入会はアンリ・カルティエ＝ブレッソンが「これはアンチ・ドキュメンタリーだ」と強く反対したことで知られ、最終的に僅差の多数決で承認された*1。1990年代以降はグローバリゼーションと消費文化の均質化——世界各地のビュッフェ・土産物屋・観光客——を撮り続け、約60冊のフォトブックを刊行してフォトブック文化の普及にも尽力した*3。2015年に設立したマーティン・パー財団はブリストルを拠点として英国・アイルランド写真史のアーカイブ収集と公開に取り組む*4。2021年にCBE（コマンダー・オブ・ザ・ブリティッシュ・エンパイア）を受章し、2025年に73歳で逝去した*1。作品はテート・モダン・ポンピドゥーセンター・V&A博物館などの主要コレクションに収蔵されており、英国の日常を最も鋭く批評した写真家として国際的に位置づけられている*1。2013〜17年にはマグナム・フォトスの会長を務めた*2。',
      citations: [
        { num: 1, name: 'Wikipedia — Martin Parr', url: 'https://en.wikipedia.org/wiki/Martin_Parr' },
        { num: 2, name: 'Magnum Photos — Martin Parr', url: 'https://www.magnumphotos.com/photographer/martin-parr/' },
        { num: 3, name: 'Photography Now — Martin Parr', url: 'https://photography-now.com/exhibition/martin_parr' },
        { num: 4, name: 'Martin Parr Foundation', url: 'https://martinparrfoundation.org/' }
      ]
    }
  },

  {
    id: 'becher',
    name: 'Bernd & Hilla Becher',
    nameJa: 'ベルント＆ヒラ・ベッヒャー',
    nationality: 'DE',
    flag: '🇩🇪',
    years: '1931–2007 / 1934–2022',
    era: '1980',
    movements: ['タイポロジー写真', 'コンセプチュアルアート', 'デュッセルドルフ派'],
    thumbnail: '',
    links: [
      { label: 'Wikipedia (EN)', url: 'https://en.wikipedia.org/wiki/Bernd_%26_Hilla_Becher' },
      { label: 'Tate — Bernd and Hilla Becher', url: 'https://www.tate.org.uk/art/artists/bernd-and-hilla-becher-718' },
    ],
    amazon: '',
    context: {
      text: 'ベルント（1931〜2007）とヒラ（1934〜2022）のベッヒャー夫妻はデュッセルドルフ芸術アカデミーで出会い、1959年から共同制作を開始した*1。20世紀後半に急速に消えゆくドイツ・ルール工業地帯の産業建築——水塔・溶鉱炉・ガスタンク・炭鉱の捲揚機・石灰窯——を記録するため、常に曇天・正面・同一スケール・モノクロ・人物なしという厳格な条件で撮影し、同一類型の複数作品をグリッド状に並べた「タイポロジー・シート」として提示した*2。この手法は個々の建造物の個性よりも類型としての共通性と差異を浮かび上がらせることで、デュシャンのレディメイドと共鳴する「匿名の彫刻」という概念を写真に持ち込み、記録と美術の境界を問い直した*1。1969年の作品集『匿名の彫刻』が美術界の注目を集め、1990年のヴェネツィア・ビエンナーレでは彫刻部門の金獅子賞を受賞——写真作品への彫刻部門初授与として記録されており、「写真が彫刻と同等の芸術的地位を持つ」という認識の転換点とされる*1。1976年よりデュッセルドルフ芸術アカデミーで教鞭をとったベルントのもとには、アンドレアス・グルスキー・トーマス・シュトゥルート・トーマス・ルフ・カンディダ・ヘーファーら後に「デュッセルドルフ派」と称される世代が集い、1990年代以降の大判カラー写真市場を形成した*3。撮影した多くの産業建築はのちに解体されており、作品が「最後の目撃者」として文化遺産的価値を持つとされる所以でもある*2。2002年エラスムス賞・2004年ハッセルブラッド賞を受賞し、作品はMoMA・テート・シカゴ美術館ほか世界の主要美術館に収蔵されている*4。1972年のカッセル・ドクメンタ5への参加がヨーロッパ美術界での地位を確立し、ミニマリズムやコンセプチュアルアートの文脈で早くから評価されたことがタイポロジーの方法論を美術史の中に定着させた*1。また1960〜70年代に撮影範囲をドイツ・ルール地方から英国・フランス・ベルギー・米国へと広げたことで、産業遺産の記録はヨーロッパと北米にまたがる比較建築史的な意味を持つようになった*2。撮影フィルムと写真集は世界の研究者・建築家・産業考古学者に参照されており、産業遺産保護の文脈でも重要な記録資料として位置づけられている*2。夫妻の遺産はデュッセルドルフ芸術大学に設立されたベッヒャー・アーカイブに引き継がれ、今日も写真研究者に公開されている*4。',
      citations: [
        { num: 1, name: 'Wikipedia — Bernd and Hilla Becher', url: 'https://en.wikipedia.org/wiki/Bernd_%26_Hilla_Becher' },
        { num: 2, name: 'Tate — Bernd and Hilla Becher', url: 'https://www.tate.org.uk/art/artists/bernd-and-hilla-becher-718' },
        { num: 3, name: 'Guggenheim — Bernd and Hilla Becher', url: 'https://www.guggenheim.org/artwork/artist/bernd-and-hilla-becher' },
        { num: 4, name: 'Hasselblad Foundation — Bernd and Hilla Becher', url: 'https://hasselbladfoundation.org/wp/laureates/bernd-och-hilla-becher/' }
      ]
    }
  },

];
