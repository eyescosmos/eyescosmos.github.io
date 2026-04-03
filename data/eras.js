const ERAS = [
  {
    id: '1839',
    period: '1839 — 1860s',
    title: '黎明期：帝国主義と写真の誕生',
    titleEn: 'Origins: Imperialism and the Birth of Photography',
    worldEvents: {
      text: 'ヨーロッパ列強が資源を求めてアジア・アフリカへ植民地を拡大した時代。清がアヘン戦争（1839–42年）で敗北し香港を割譲。1848年「諸国民の春」の革命がヨーロッパを席巻し、1853–56年のクリミア戦争、1857年インド大反乱、1861–65年の南北戦争と戦乱が続いた。技術面では1851年スコット・アーチャーが湿板コロジオン法を発表して露光時間を劇的に短縮し、戦場での撮影を可能にした。1844年モールスが有線電信を実用化し、報道とビジュアルが連動する土台が生まれた。',
      textEn: 'European empires expanded into Asia and Africa in search of resources. Qing China was defeated in the Opium Wars (1839–42) and ceded Hong Kong. The revolutions of 1848 swept across Europe, followed by the Crimean War (1853–56), the Indian Rebellion of 1857, and the American Civil War (1861–65). Technologically, Frederick Scott Archer announced the wet collodion process in 1851, dramatically shortening exposure times and making battlefield photography possible. Morse’s telegraph, put into practical use in 1844, also laid the groundwork for modern news circulation in which text and images moved together.',
      sources: [
        { text: 'Britannica — Opium Wars', url: 'https://www.britannica.com/topic/Opium-Wars' },
        { text: 'CFR Education — Industrialization and Imperialism', url: 'https://education.cfr.org/learn/learning-journey/contemporary-history-pre-1900-industrialization-and-imperialism/what-are-the-causes-and-consequences-of-industrialization' },
      ]
    },
    photoContext: {
      text: '写真家たちは植民地の軍隊・行政官とともに中東・アジア・南米へ渡り、「異国の文化」をヨーロッパ人に見せた。技術的には、ダゲレオタイプ（一点物の銀板写真）からカロタイプ（紙ネガによる複製可能な写真）、さらにスコット・アーチャーが1851年に発表した湿板コロジオン法へと急速に進化した。湿板法は露光時間を大幅に短縮しポートレート撮影を可能にしたが、撮影直前に薬品を塗布する必要があり、現場での暗室作業が不可欠だった。写真は植民地において「中立な記録」ではなく、支配の物語を構築・正当化する装置として機能した。',
      textEn: 'Photographers travelled with colonial armies and administrators through the Middle East, Asia, and South America, producing images of “foreign cultures” for European viewers. The medium evolved quickly from the daguerreotype, a unique image on silvered copper, to the calotype, which allowed multiple prints from a paper negative, and then to Archer’s wet collodion process. Wet plates made shorter exposures and portrait work possible, but they still required chemistry to be prepared on site, so darkroom labor remained inseparable from fieldwork. In colonial settings, photography did not function as a neutral record; it often helped construct and legitimize narratives of imperial rule.',
      sources: [
        { text: 'Britannica — History of Photography', url: 'https://www.britannica.com/technology/photography/Photographys-early-evolution-c-1840-c-1900' },
        { text: 'Taylor & Francis — Photography, Colonialism, and War', url: 'https://www.tandfonline.com/doi/full/10.1080/07292473.2025.2463752' },
        { text: 'Photoworks — Images and Imperialism', url: 'https://photoworks.org.uk/images-and-imperialism-a-photographic-record-of-british-india/' },
      ]
    }
  },

  {
    id: '1870',
    period: '1870 — 1890s',
    title: '産業化・社会改革・写真の大衆化',
    titleEn: 'Industrialization, Social Reform, and Mass Photography',
    worldEvents: {
      text: '普仏戦争（1870–71年）でフランスが敗北しドイツ帝国が誕生。パリ・コミューン（1871年）は72日で鎮圧され、1873年恐慌が欧米で大規模な労働運動を引き起こした。アメリカでは「金ぴか時代」の急速な工業化と大量移民で都市過密化が進んだ。1884–85年のベルリン会議でアフリカ分割が制度化された。技術面では1871年リチャード・マドックスがゼラチン乾板を発明し撮影直前の薬品塗布が不要に。1880年ニューヨーク・デイリー・グラフィック紙がハーフトーン印刷で写真を新聞掲載し、1888年コダックカメラが大衆写真を開いた。',
      textEn: 'France lost the Franco-Prussian War (1870–71), and the German Empire was founded. The Paris Commune of 1871 was violently suppressed after seventy-two days, while the Panic of 1873 triggered large labor movements across Europe and the United States. In America, rapid industrialization and migration during the Gilded Age intensified urban overcrowding. The Berlin Conference of 1884–85 formalized the partition of Africa. In photography, Richard Maddox invented the gelatin dry plate in 1871, removing the need to coat plates immediately before exposure. Halftone printing brought photographs into newspapers by 1880, and Kodak’s camera of 1888 opened picture-making to a mass public.',
      sources: [
        { text: 'Britannica — Franco-Prussian War', url: 'https://www.britannica.com/event/Franco-German-War' },
        { text: 'Wikipedia — Paris Commune', url: 'https://en.wikipedia.org/wiki/Paris_Commune' },
        { text: 'Britannica — Scramble for Africa', url: 'https://www.britannica.com/event/Scramble-for-Africa' },
      ]
    },
    photoContext: {
      text: 'リチャード・マドックスが1871年にゼラチン乾板を発明したことで、撮影直前の薬品塗布が不要になり写真の携帯性が飛躍的に向上した。1888年、ジョージ・イーストマンがロールフィルム内蔵の「コダック」カメラを発売し、「ボタンを押すだけ」の写真撮影を一般大衆に開放した（「You press the button, we do the rest」）。社会的には、移民・スラム・児童労働などを記録するドキュメンタリー写真の先駆けが生まれた。科学の分野ではマイブリッジとマレーが連続写真で運動の解析を行い、後の映画誕生への道を開いた。',
      textEn: 'Maddox’s dry plate transformed photography into a more portable practice because photographers no longer needed to prepare chemicals moments before exposure. In 1888, George Eastman introduced the Kodak camera with roll film and marketed it with the promise, “You press the button, we do the rest,” turning photography into an everyday consumer practice. Socially, this was also the period in which early documentary photography emerged to record immigration, slums, and child labor. In scientific work, Muybridge and Marey used sequential photography to analyze motion, helping to open the path toward cinema.',
      sources: [
        { text: 'Britannica — History of Photography', url: 'https://www.britannica.com/technology/photography' },
        { text: 'George Eastman Museum — Kodak and the Democratization of Photography', url: 'https://www.eastman.org/george-eastman' },
        { text: 'Wikipedia — Dry plate', url: 'https://en.wikipedia.org/wiki/Dry_plate' },
      ]
    }
  },
  {
    id: '1890',
    period: '1890 — 1910s',
    title: 'ピクトリアリズム全盛・写真分離派・世紀転換期',
    titleEn: 'The High Tide of Pictorialism, Photo-Secession, and the Turn of the Century',
    worldEvents: {
      text: '日清戦争（1894–95年）・米西戦争（1898年）・ボーア戦争（1899–1902年）・日露戦争（1904–05年）と列強の衝突が続いた。日露戦争での日本の勝利は白人列強「不敗」神話を崩し、アジア各地のナショナリズムを刺激した。1905年ロシア第一革命、1910年日韓併合・メキシコ革命と激動の時代。技術面では1895年レントゲンのX線発見が「見えないものを可視化する」写真の可能性を拡大。1895年リュミエール兄弟が映画を公開し、動く写真が誕生。リュミエール兄弟が発明したオートクローム（1904年特許・1907年商業発売）が世界初の実用的カラー写真技術として登場した。',
      textEn: 'The First Sino-Japanese War (1894–95), the Spanish-American War (1898), the Boer War (1899–1902), and the Russo-Japanese War (1904–05) marked a period of constant imperial conflict. Japan’s victory over Russia shattered the myth of white imperial invincibility and energized nationalist movements across Asia. The First Russian Revolution broke out in 1905, while Japan formally annexed Korea and the Mexican Revolution began in 1910. Technologically, Wilhelm Rontgen’s discovery of X-rays in 1895 expanded the photographic imagination toward things the eye could not see. In the same year the Lumiere brothers publicly projected motion pictures, and their Autochrome process, patented in 1904 and sold commercially from 1907, became the first practical color photography system.',
      sources: [
        { text: 'Britannica — First Sino-Japanese War', url: 'https://www.britannica.com/event/First-Sino-Japanese-War' },
        { text: 'Britannica — Spanish-American War', url: 'https://www.britannica.com/event/Spanish-American-War' },
        { text: 'Britannica — Russo-Japanese War', url: 'https://www.britannica.com/event/Russo-Japanese-War' },
        { text: 'Wikipedia — 1900s', url: 'https://en.wikipedia.org/wiki/1900s' },
      ]
    },
    photoContext: {
      text: 'ピクトリアリズムは、写真を絵画と同等の芸術として位置づけるため、ソフトフォーカス・ゴム重クロム酸塩プリント・プラチナプリント・オイルプリントなど手工芸的技法を駆使した国際運動の最盛期を迎えた。イギリスでは「リンクト・リング（Linked Ring Brotherhood）」（1892年）、フランスでは「フォト・クラブ・ド・パリ」が芸術写真を推進した。アメリカではアルフレッド・スティーグリッツが1902年に「写真分離派（Photo-Secession）」を結成し、1903年には高品質写真誌『カメラ・ワーク（Camera Work）』を創刊した。1905年にニューヨーク五番街に開廊した「ギャラリー291」は、芸術写真に加えマティス・ピカソらのヨーロッパ前衛美術をアメリカで初めて紹介する場となった。一方でP.H.エマーソンの「自然主義写真論」（1889年）は、合成・操作を排した自然記録の倫理を提唱し、後のストレート写真への伏線となった。',
      textEn: 'Pictorialism reached its international peak as photographers used handcrafted techniques such as soft focus, gum bichromate printing, platinum printing, and oil printing to claim photography as an art equal to painting. In Britain the Linked Ring Brotherhood, founded in 1892, championed artistic photography, while in France the Photo-Club de Paris pursued similar aims. In the United States, Alfred Stieglitz formed the Photo-Secession in 1902 and launched the high-quality journal Camera Work in 1903. His gallery at 291 Fifth Avenue, opened in 1905, became a crucial site where artistic photography and European modernists such as Matisse and Picasso were introduced to American audiences. At the same time, P. H. Emerson’s naturalistic theory of photography, articulated in 1889, argued for an unmanipulated record of the world and helped lay the groundwork for later straight photography.',
      sources: [
        { text: 'Britannica — Pictorialism', url: 'https://www.britannica.com/technology/Pictorialism' },
        { text: 'The Art Story — Pictorialism', url: 'https://www.theartstory.org/movement/pictorialism/' },
        { text: 'Smarthistory — 291 Little Galleries of the Photo-Secession', url: 'https://smarthistory.org/291-stieglitz/' },
        { text: 'Wikipedia — Camera Work', url: 'https://en.wikipedia.org/wiki/Camera_Work' },
      ]
    }
  }
  ,{
    id: '1910',
    period: '1910 — 1920s',
    title: 'モダニズムの台頭：大戦・ダダ・ストレート写真',
    titleEn: 'The Rise of Modernism: World War, Dada, and Straight Photography',
    worldEvents: {
      text: '第一次世界大戦（1914–18年）は機関銃・毒ガス・航空機による「工業化された大量死」として、過去のあらゆる戦争と次元の異なる惨禍をもたらした。1917年にはロシア革命が勃発しロマノフ朝が崩壊、史上初の社会主義国家ソビエトが誕生した。同年アメリカが参戦し、戦後のヴェルサイユ体制はドイツに苛酷な賠償を課した。文化面では1916年チューリッヒのカバレー・ヴォルテールでダダが誕生し、理性・進歩・国家への根本的な懐疑が前衛芸術として噴出した。1919年にはバウハウスがヴァイマールに開校し、美術・工芸・建築・写真の統合的教育が始まった。アメリカでは「狂騒の20年代」と大量消費社会の到来が、写真を広告・ファッション・報道の主要メディアとして確立させた。',
      textEn: 'World War I (1914–18) brought an unprecedented scale of industrialized death through machine guns, poison gas, and aircraft. The Russian Revolution of 1917 toppled the Romanov dynasty and created the first socialist state, while the United States entered the war and the postwar Versailles order imposed severe reparations on Germany. In culture, Dada emerged at Zurich’s Cabaret Voltaire in 1916, turning radical doubt toward reason, progress, and nationalism into avant-garde practice. In 1919 the Bauhaus opened in Weimar and began its integrated approach to art, craft, architecture, and photography. In the United States, the mass consumer culture of the Roaring Twenties helped establish photography as a central medium for advertising, fashion, and illustrated news.',
      sources: [
        { text: 'Britannica — World War I', url: 'https://www.britannica.com/event/World-War-I' },
        { text: 'Wikipedia — Bauhaus', url: 'https://en.wikipedia.org/wiki/Bauhaus' },
        { text: 'Britannica — Dada', url: 'https://www.britannica.com/art/Dada' },
      ]
    },
    photoContext: {
      text: 'アメリカではポール・ストランドが1916–17年にピクトリアリズムを決定的に離れ、幾何学的構成と直接的なフォーカスによる「ストレート写真」を確立した。スティーグリッツは『カメラ・ワーク』誌（1917年最終号）でストランドの仕事を「これまで写真界に現れた最も直接的な表現」と評した。ダダとシュルレアリスムの文脈では、マン・レイがカメラなしで印画紙に直接像を作る「レイオグラフ」（1921年）を発明し、写真の「記録」という定義を根底から問い直した。ドイツではバウハウスのモホイ＝ナジが俯瞰・仰角・フォトグラムによる「新しいヴィジョン」を理論化し、ザンダーは20世紀のドイツ社会の全階層を組織的に肖像記録する「人類の生理学的アルバム」プロジェクトを開始した。',
      textEn: 'In the United States, Paul Strand decisively broke with pictorialism in 1916–17 and helped define straight photography through sharp focus and geometric composition. In the final issue of Camera Work in 1917, Stieglitz described Strand’s work as the most direct expression photography had yet produced. In the context of Dada and Surrealism, Man Ray invented the rayograph in 1921 by placing objects directly on photographic paper without a camera, forcing a rethinking of photography as record. In Germany, Laszlo Moholy-Nagy theorized a New Vision built on bird’s-eye views, steep angles, and photograms, while August Sander began his vast project of systematically portraying the full social spectrum of twentieth-century Germany.',
      sources: [
        { text: 'Smarthistory — Paul Strand', url: 'https://smarthistory.org/paul-strand-blind-woman/' },
        { text: 'MoMA — Photography and Modernism', url: 'https://www.moma.org/collection/works?classification=photography&date_begin=1910&date_end=1929' },
        { text: 'Wikipedia — Neue Sachlichkeit', url: 'https://en.wikipedia.org/wiki/Neue_Sachlichkeit' },
      ]
    }
  }
 ,{
    id: '1930',
    period: '1930 — 1940s',
    title: '大恐慌・ファシズム・第二次世界大戦',
    titleEn: 'The Great Depression, Fascism, and World War II',
    worldEvents: {
      text: '1929年のウォール街株式市場暴落を発端とする大恐慌は欧米を席巻し、アメリカでは失業者が1500万人を超えた。ルーズベルト政権のニューディール政策（1933年〜）が雇用・農業・インフラ支援を実施。ヨーロッパではファシズムが台頭し、1933年ヒトラーがドイツ首相に就任、1936年スペイン内戦、1937年日中戦争勃発、1939年第二次世界大戦開始と戦火が拡大した。1941年の真珠湾攻撃でアメリカが参戦。1945年8月の広島・長崎への原子爆弾投下で大戦は終結した。ホロコーストによるユダヤ人約600万人の虐殺が連合国軍の進軍によって記録された。',
      textEn: 'The Great Depression, triggered by the Wall Street crash of 1929, spread across Europe and North America; in the United States unemployment climbed above fifteen million. Roosevelt’s New Deal, launched in 1933, sought relief through labor, agricultural, and infrastructure programs. In Europe, fascism rose rapidly: Hitler became German chancellor in 1933, the Spanish Civil War began in 1936, war broke out between China and Japan in 1937, and World War II started in 1939. The United States entered the conflict after Pearl Harbor in 1941. The war ended in August 1945 after the atomic bombings of Hiroshima and Nagasaki, while the murder of roughly six million Jews in the Holocaust was documented as Allied forces advanced through Europe.',
      sources: [
        { text: 'Britannica — Great Depression', url: 'https://www.britannica.com/event/Great-Depression' },
        { text: 'Wikipedia — World War II', url: 'https://en.wikipedia.org/wiki/World_War_II' },
        { text: 'Britannica — New Deal', url: 'https://www.britannica.com/event/New-Deal' },
      ]
    },
    photoContext: {
      text: 'ルーズベルト政権のFSA（農業安定局）写真プロジェクト（1935–44年）ではロイ・ストライカーの指揮下でラング・エヴァンスら8名が農村の窮状を組織的に記録し、約17万枚の写真を残した。1936年創刊のLIFE誌は写真報道誌として急成長し、毎週数百万部を売る「写真が報道を担う」時代を開いた。第二次世界大戦では従軍写真家が連合国の情報戦・戦意高揚に組み込まれる一方、硫黄島の星条旗（ジョー・ローゼンタール）など個々の写真が戦争の象徴として流通した。1947年に戦場写真家キャパ・カルティエ＝ブレッソン・ロジャーら5名がマグナム・フォトを設立し、独立系フォトエージェンシーとして写真家の権利と著作権を守る組織モデルを生んだ。',
      textEn: 'Within Roosevelt’s Farm Security Administration photography project (1935–44), Roy Stryker directed a team including Dorothea Lange and Walker Evans to systematically record rural poverty, leaving behind roughly 170,000 images. LIFE magazine, launched in 1936, grew rapidly into a mass photojournalism weekly that sold millions of copies and normalized the idea that photographs could carry news on their own. During World War II, embedded photographers became part of Allied propaganda and information systems, while pictures such as Joe Rosenthal’s raising of the flag on Iwo Jima circulated as symbols of the war itself. In 1947 Robert Capa, Henri Cartier-Bresson, George Rodger, and others founded Magnum Photos, establishing an independent agency model that defended photographers’ authorship and copyrights.',
      sources: [
        { text: 'Library of Congress — FSA/OWI Collection', url: 'https://www.loc.gov/pictures/collection/fsa/' },
        { text: 'Wikipedia — LIFE magazine', url: 'https://en.wikipedia.org/wiki/Life_(magazine)' },
        { text: 'Magnum Photos — About Magnum', url: 'https://www.magnumphotos.com/about-magnum/history/' },
      ]
    }
  },{
    id: '1950',
    period: '1950 — 1960s',
    title: '戦後・冷戦・公民権運動',
    titleEn: 'Postwar Reconstruction, the Cold War, and Civil Rights',
    worldEvents: {
      text: '冷戦の幕開けとともに核の恐怖が世界を覆った。朝鮮戦争（1950–53年）・キューバ危機（1962年）・ベトナム戦争介入（1964年〜）とアメリカの関与が続いた。アジア・アフリカでは植民地独立運動が相次ぎ、1960年の「アフリカの年」には17カ国が独立した。アメリカでは1955年のロサ・パークス事件から公民権運動が高まり、1963年キング牧師「I Have a Dream」演説・1964年公民権法制定へと至った。1957年のスプートニク打上げに始まる米ソ宇宙開発競争は科学技術への楽観と核の恐怖の同居を象徴した。',
      textEn: 'As the Cold War began, the threat of nuclear annihilation hung over global politics. The Korean War (1950–53), the Cuban Missile Crisis (1962), and escalating U.S. involvement in Vietnam from 1964 onward made American power central to postwar conflict. Across Asia and Africa, decolonization accelerated; in the “Year of Africa” in 1960 alone, seventeen countries gained independence. In the United States, the civil rights movement rose from events such as Rosa Parks’s arrest in 1955 toward Martin Luther King Jr.’s “I Have a Dream” speech in 1963 and the Civil Rights Act of 1964. The space race, launched symbolically by Sputnik in 1957, condensed both technological optimism and the dread of military escalation.',
      sources: [
        { text: 'Britannica — Cold War', url: 'https://www.britannica.com/event/Cold-War' },
        { text: 'Wikipedia — Civil Rights Movement', url: 'https://en.wikipedia.org/wiki/Civil_rights_movement' },
        { text: 'Britannica — Decolonization', url: 'https://www.britannica.com/topic/decolonization' },
      ]
    },
    photoContext: {
      text: '1950年代のLIFE誌（最盛期の発行部数850万部）は写真報道の頂点に立ったが、テレビの普及とともにその地位が揺らぎ始めた。ロバート・フランクの「The Americans」（1958/59年）はLIFE的な明朗さを否定する暗さ・粒子感・傾いた水平線で、戦後アメリカ写真の転換点となった。日本では1958年に東松照明・川田喜久治らがVIVO（写真家集団）を結成し「日本の戦後」を記録。1968–70年の「プロヴォーク」誌（中平卓馬・森山大道・多木浩二ら）は「アレ・ブレ・ボケ」の美学を提唱し、日本写真の国際的評価の起点となった。写真家が著作権を持つマグナム・モデルが定着し、フォトジャーナリストが固有の視点を持つ「作者」として評価される文化が形成された。',
      textEn: 'In the 1950s, LIFE magazine, with a peak circulation of 8.5 million, stood at the summit of photojournalism, though television was already beginning to erode its dominance. Robert Frank’s The Americans (1958/59), with its darkness, grain, and tilted horizons, rejected the optimistic tone associated with LIFE and marked a turning point in postwar American photography. In Japan, Shomei Tomatsu, Kikuji Kawada, and others formed the photographers’ collective VIVO in 1958 to record the realities of the postwar nation. The magazine Provoke (1968–70), associated with Takuma Nakahira, Daido Moriyama, and Koji Taki, articulated the rough “are, bure, boke” aesthetic that became a key reference in the international reception of Japanese photography. Meanwhile, the Magnum model normalized the idea of the photojournalist as an authored viewpoint rather than a mere anonymous recorder.',
      sources: [
        { text: 'Wikipedia — The Americans', url: 'https://en.wikipedia.org/wiki/The_Americans' },
        { text: 'Wikipedia — Provoke (magazine)', url: 'https://en.wikipedia.org/wiki/Provoke_(magazine)' },
        { text: 'MoMA — New Japanese Photography 1974', url: 'https://www.moma.org/calendar/exhibitions/2576' },
      ]
    }
  },{
    id: '1970',
    period: '1970 — 1980s',
    title: 'コンセプチュアルアート・フェミニズム・ポストモダン',
    titleEn: 'Conceptual Art, Feminism, and Postmodernism',
    worldEvents: {
      text: 'ベトナム戦争は1975年のサイゴン陥落まで続き、テレビ放送された映像が反戦世論を形成した。第二波フェミニズム運動（1960年代後半〜）は女性の表象・身体・労働の権利を政治化した。1981年にAIDS危機が始まりニューヨーク・サンフランシスコのゲイコミュニティを直撃。レーガン政権（1981–89年）とサッチャー政権（1979–90年）の新自由主義が福祉国家を後退させた。1979年のイラン・イスラム革命・ニカラグア革命と第三世界の政治変動が続き、1989年のベルリンの壁崩壊が冷戦の終焉を告げた。メディア環境の飽和が「イメージそのものを問う」思想（ポストモダン）を生んだ。',
      textEn: 'The Vietnam War continued until the fall of Saigon in 1975, and televised images played a major role in shaping antiwar opinion. Second-wave feminism, emerging from the late 1960s onward, politicized representation, the body, and women’s labor. The AIDS crisis began in 1981 and devastated queer communities in New York and San Francisco. The neoliberal policies of the Reagan administration (1981–89) and Thatcher government (1979–90) rolled back the welfare state, while the Iranian Revolution of 1979, the Nicaraguan Revolution, and other political upheavals reshaped the so-called Third World. The fall of the Berlin Wall in 1989 signaled the end of the Cold War. In this saturated media environment, postmodern thought increasingly turned toward the image itself as an object of critique.',
      sources: [
        { text: 'Wikipedia — Second-wave feminism', url: 'https://en.wikipedia.org/wiki/Second-wave_feminism' },
        { text: 'Wikipedia — AIDS epidemic', url: 'https://en.wikipedia.org/wiki/HIV/AIDS_in_the_United_States' },
        { text: 'Wikipedia — Fall of the Berlin Wall', url: 'https://en.wikipedia.org/wiki/Fall_of_the_Berlin_Wall' },
      ]
    },
    photoContext: {
      text: '写真が美術館・ギャラリーで「ファインアート」として展示・売買される市場が1970年代のニューヨークで確立した。1977年のダグラス・クリンプによる「ピクチャーズ」展（Artists Space）はシャーマン・レヴィン・プリンスらの「イメージの盗用・引用」を「ピクチャーズ世代」として概念化し、広告・映画・テレビのイメージを流用することで視覚表象の構造自体を批評の対象とした。1976年のMoMAにおけるウィリアム・エグルストン個展は、カラー写真がファインアートとして美術館に入った最初の主要な事例となった。日本では「プロヴォーク」後に森山大道・荒木経惟らが各自の方向へ展開し、「私写真」と呼ばれる私的なドキュメントの潮流が生まれた。',
      textEn: 'In 1970s New York, a market emerged in which photography was exhibited and sold in museums and galleries as fine art. Douglas Crimp’s 1977 exhibition Pictures at Artists Space grouped artists such as Cindy Sherman, Sherrie Levine, and Richard Prince under what became known as the Pictures Generation, framing appropriation and quotation as ways to critique the structure of visual representation itself across advertising, cinema, and television. William Eggleston’s 1976 exhibition at MoMA became an early landmark in the museum acceptance of color photography as fine art. In Japan, after Provoke, figures such as Daido Moriyama and Nobuyoshi Araki moved in different directions, contributing to the rise of an intimate documentary current often described as shi-shashin, or “I-photography.”',
      sources: [
        { text: 'Wikipedia — Pictures Generation', url: 'https://en.wikipedia.org/wiki/Pictures_Generation' },
        { text: 'MoMA — William Eggleston\'s Guide (1976)', url: 'https://www.moma.org/calendar/exhibitions/2531' },
        { text: 'Wikipedia — Provoke (magazine)', url: 'https://en.wikipedia.org/wiki/Provoke_(magazine)' },
      ]
    }
  },

  {
    id: '1980',
    period: '1980 — 1990s',
    title: 'デュッセルドルフ派・エイズ危機・デジタル革命前夜',
    titleEn: 'The Dusseldorf School, the AIDS Crisis, and the Eve of the Digital Revolution',
    worldEvents: {
      text: '1981年に報告されたAIDS危機はニューヨーク・サンフランシスコのゲイコミュニティと芸術家集団を直撃し、政府の不作為への怒りがACT UP（1987年結成）などの直接行動運動を生んだ。1986年のチェルノブイリ原発事故は技術への信頼を揺るがし、フィリピンではコラソン・アキノ支持者の写真証拠がマルコス政権崩壊を後押しした。1989年の天安門事件・ベルリンの壁崩壊・東欧革命の連鎖はテレビとフォトジャーナリズムによってリアルタイムで世界に届けられた。レーガン・サッチャー体制のネオリベラリズムは格差を拡大し、失業・貧困・炭鉱閉鎖に直面する労働者階級の姿を記録する社会的ドキュメンタリーへの需要を生んだ。',
      textEn: 'The AIDS crisis, first reported in 1981, struck queer communities and artistic circles in New York and San Francisco, and anger over official inaction fueled direct-action movements such as ACT UP, founded in 1987. The Chernobyl disaster of 1986 shook public faith in technological progress, while in the Philippines photographic evidence circulated by supporters of Corazon Aquino helped undermine the Marcos regime. The Tiananmen protests of 1989, the fall of the Berlin Wall, and the revolutions across Eastern Europe were transmitted worldwide in near real time through television and photojournalism. Under Reagan and Thatcher, neoliberal reforms widened inequality and helped generate a renewed demand for social documentary images of labor, unemployment, poverty, and deindustrialization.',
      sources: [
        { text: 'Wikipedia — ACT UP', url: 'https://en.wikipedia.org/wiki/ACT_UP' },
        { text: 'Wikipedia — Chernobyl disaster', url: 'https://en.wikipedia.org/wiki/Chernobyl_disaster' },
        { text: 'Wikipedia — Tiananmen Square protests', url: 'https://en.wikipedia.org/wiki/1989_Tiananmen_Square_protests_and_massacre' },
      ]
    },
    photoContext: {
      text: '1970年代後半にデュッセルドルフ芸術アカデミーでベッヒャー夫妻の薫陶を受けたアンドレアス・グルスキー・トーマス・シュトゥルート・トーマス・ルフらは「デュッセルドルフ派」として大判カメラ・カラーフィルム・大型プリントの組み合わせで資本主義の空間を冷静に記録し、1980年代の美術市場で写真を絵画と同等のコレクタブルへと押し上げた。ナン・ゴールディンは日記的スライドショー『性的依存のバラッド』（1986年）でエイズ禍中のニューヨーク下位文化を内側から記録し、「外部の視点なき証言写真」の可能性を示した。アドビ社がPhotoshopを1990年にリリースしたことで写真と現実の対応関係は制度的な前提から問われる対象へと変わり、「写真は真実か」という問いがデジタル時代に再燃した。',
      textEn: 'Artists such as Andreas Gursky, Thomas Struth, and Thomas Ruff, who studied under Bernd and Hilla Becher at the Kunstakademie Dusseldorf in the late 1970s, became associated with the Dusseldorf School. Using large-format cameras, color film, and monumental prints, they coolly described the spaces of late capitalism and helped elevate photography into a collectible medium on par with painting in the 1980s art market. Nan Goldin’s diary-like slide installation The Ballad of Sexual Dependency (1986) recorded New York subcultures from within during the AIDS crisis and showed what testimonial photography could look like without an external, supposedly neutral viewpoint. When Adobe released Photoshop in 1990, the assumed bond between photograph and reality became newly unstable, and the question “Is photography true?” returned with force in the digital era.',
      sources: [
        { text: 'Wikipedia — Düsseldorf School of Photography', url: 'https://en.wikipedia.org/wiki/D%C3%BCsseldorf_School_of_Photography' },
        { text: 'Wikipedia — Nan Goldin', url: 'https://en.wikipedia.org/wiki/Nan_Goldin' },
        { text: 'Wikipedia — Adobe Photoshop', url: 'https://en.wikipedia.org/wiki/Adobe_Photoshop' },
      ]
    }
  }
  /* 次のセクションは順次追加 */
];
