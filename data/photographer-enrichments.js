const PHOTOGRAPHER_ENRICHMENTS = {
  stieglitz: {
    descriptorJa: '近代写真',
    descriptorEn: 'Modern Photography',
    keywordsJa: '291、写真分離派、ストレート写真への転換',
    keywordsEn: '291, Photo-Secession, and the shift toward straight photography',
    representativeWorkJa: '《エクイヴァレンツ》',
    representativeWorkEn: 'Equivalents',
    extraMovements: ['モダニズム'],
    relatedPeople: [
      {
        nameJa: 'ジョージア・オキーフ',
        nameEn: "Georgia O'Keeffe",
        roleJa: '画家',
        roleEn: 'Artist',
        urlEn: 'https://en.wikipedia.org/wiki/Georgia_O%27Keeffe'
      },
      {
        nameJa: 'サダキチ・ハートマン',
        nameEn: 'Sadakichi Hartmann',
        roleJa: '批評家',
        roleEn: 'Critic',
        urlEn: 'https://en.wikipedia.org/wiki/Sadakichi_Hartmann'
      }
    ]
  },
  strand: {
    descriptorJa: '近代写真',
    descriptorEn: 'Modern Photography',
    keywordsJa: '291、ストレート写真、モダニズム',
    keywordsEn: '291, straight photography, and modernism',
    representativeWorkJa: '『Wall Street』',
    representativeWorkEn: 'Wall Street',
    relatedPeople: [
      {
        nameJa: 'アルフレッド・スティーグリッツ',
        nameEn: 'Alfred Stieglitz',
        photographerId: 'stieglitz'
      },
      {
        nameJa: 'セザンヌ',
        nameEn: 'Paul Cezanne',
        roleJa: '画家',
        roleEn: 'Artist',
        urlEn: 'https://en.wikipedia.org/wiki/Paul_C%C3%A9zanne'
      }
    ]
  },
  beato: {
    descriptorJa: '幕末・明治視覚文化',
    descriptorEn: 'Meiji Visual Culture',
    keywordsJa: '幕末日本、手彩色写真、横浜写真',
    keywordsEn: 'Bakumatsu Japan, hand-colored photography, and Yokohama albums',
    representativeWorkJa: '『Views of Japan』',
    representativeWorkEn: 'Views of Japan',
    relatedPeople: [
      {
        nameJa: 'チャールズ・ウィルグマン',
        nameEn: 'Charles Wirgman',
        roleJa: '挿絵記者',
        roleEn: 'Illustrator',
        urlEn: 'https://en.wikipedia.org/wiki/Charles_Wirgman'
      }
    ]
  },
  domon: {
    descriptorJa: '日本リアリズム写真',
    descriptorEn: 'Japanese Realism',
    keywordsJa: '日本写真、リアリズム、戦後写真',
    keywordsEn: 'Japanese photography, realism, and postwar photography',
    representativeWorkJa: '『ヒロシマ』',
    representativeWorkEn: 'Hiroshima',
    extraMovements: ['ドキュメンタリー'],
    relatedPeople: [
      {
        nameJa: '亀倉雄策',
        nameEn: 'Yusaku Kamekura',
        roleJa: 'デザイナー',
        roleEn: 'Designer',
        urlEn: 'https://en.wikipedia.org/wiki/Y%C5%ABsaku_Kamekura'
      },
      {
        nameJa: '東松照明',
        nameEn: 'Shomei Tomatsu',
        photographerId: 'tomatsu'
      }
    ]
  },
  tomatsu: {
    descriptorJa: '戦後日本写真',
    descriptorEn: 'Postwar Japanese Photography',
    keywordsJa: '戦後日本、基地、長崎、プロヴォーク以前',
    keywordsEn: 'postwar Japan, military bases, Nagasaki, and pre-Provoke photography',
    representativeWorkJa: '『Chewing Gum and Chocolate』',
    representativeWorkEn: 'Chewing Gum and Chocolate',
    relatedPeople: [
      {
        nameJa: '大江健三郎',
        nameEn: 'Kenzaburo Oe',
        roleJa: '作家',
        roleEn: 'Writer',
        urlEn: 'https://en.wikipedia.org/wiki/Kenzabur%C5%8D_%C5%8Ce'
      },
      {
        nameJa: '中平卓馬',
        nameEn: 'Takuma Nakahira',
        photographerId: 'takuma-nakahira'
      }
    ]
  },
  moriyama: {
    descriptorJa: 'プロヴォーク以後',
    descriptorEn: 'Post-Provoke Photography',
    keywordsJa: 'プロヴォーク、アレ・ブレ・ボケ、都市写真',
    keywordsEn: 'Provoke, are-bure-boke, and urban photography',
    representativeWorkJa: '『にっぽん劇場写真帖』',
    representativeWorkEn: 'Japan, a Photo Theater',
    extraMovements: ['ストリート写真'],
    relatedPeople: [
      {
        nameJa: '中平卓馬',
        nameEn: 'Takuma Nakahira',
        photographerId: 'takuma-nakahira'
      },
      {
        nameJa: '寺山修司',
        nameEn: 'Shuji Terayama',
        roleJa: '詩人・演出家',
        roleEn: 'Poet / Director',
        urlEn: 'https://en.wikipedia.org/wiki/Sh%C5%ABji_Terayama'
      }
    ]
  },
  robertfrank: {
    descriptorJa: '戦後アメリカ写真',
    descriptorEn: 'Postwar American Photography',
    keywordsJa: 'ロードトリップ、ビート、アメリカ人',
    keywordsEn: 'road trip photography, Beat culture, and The Americans',
    representativeWorkJa: '『The Americans』',
    representativeWorkEn: 'The Americans',
    extraMovements: ['ストリート写真'],
    relatedPeople: [
      {
        nameJa: 'ジャック・ケルアック',
        nameEn: 'Jack Kerouac',
        roleJa: '作家',
        roleEn: 'Writer',
        urlEn: 'https://en.wikipedia.org/wiki/Jack_Kerouac'
      }
    ]
  },
  evans: {
    descriptorJa: 'ドキュメンタリー写真',
    descriptorEn: 'Documentary Photography',
    keywordsJa: 'FSA、アメリカ写真、都市と看板',
    keywordsEn: 'FSA, American photography, and vernacular signs',
    representativeWorkJa: '『American Photographs』',
    representativeWorkEn: 'American Photographs',
    relatedPeople: [
      {
        nameJa: 'ジェームズ・エイジー',
        nameEn: 'James Agee',
        roleJa: '作家',
        roleEn: 'Writer',
        urlEn: 'https://en.wikipedia.org/wiki/James_Agee'
      }
    ]
  },
  manray: {
    descriptorJa: 'シュルレアリスム写真',
    descriptorEn: 'Surrealist Photography',
    keywordsJa: 'レイヨグラフ、ダダ、シュルレアリスム',
    keywordsEn: 'rayographs, Dada, and Surrealism',
    representativeWorkJa: '『レイヨグラフ』',
    representativeWorkEn: 'Rayographs',
    relatedPeople: [
      {
        nameJa: 'マルセル・デュシャン',
        nameEn: 'Marcel Duchamp',
        roleJa: 'アーティスト',
        roleEn: 'Artist',
        urlEn: 'https://en.wikipedia.org/wiki/Marcel_Duchamp'
      },
      {
        nameJa: 'アンドレ・ブルトン',
        nameEn: 'Andre Breton',
        roleJa: '詩人・批評家',
        roleEn: 'Poet / Critic',
        urlEn: 'https://en.wikipedia.org/wiki/Andr%C3%A9_Breton'
      }
    ]
  },
  moholy: {
    descriptorJa: 'バウハウス写真',
    descriptorEn: 'Bauhaus Photography',
    keywordsJa: 'バウハウス、新しい視覚、フォトグラム',
    keywordsEn: 'Bauhaus, New Vision, and photograms',
    representativeWorkJa: '『絵画 写真 映画』',
    representativeWorkEn: 'Painting Photography Film',
    relatedPeople: [
      {
        nameJa: 'ヴァルター・グロピウス',
        nameEn: 'Walter Gropius',
        roleJa: '建築家',
        roleEn: 'Architect',
        urlEn: 'https://en.wikipedia.org/wiki/Walter_Gropius'
      },
      {
        nameJa: 'エル・リシツキー',
        nameEn: 'El Lissitzky',
        roleJa: 'アーティスト',
        roleEn: 'Artist',
        urlEn: 'https://en.wikipedia.org/wiki/El_Lissitzky'
      }
    ]
  },
  sherman: {
    descriptorJa: 'ポストモダン写真',
    descriptorEn: 'Postmodern Photography',
    keywordsJa: 'アンタイトルド・フィルム・スティルズ、フェミニズム、演出写真',
    keywordsEn: 'Untitled Film Stills, feminism, and staged photography',
    representativeWorkJa: '『Untitled Film Stills』',
    representativeWorkEn: 'Untitled Film Stills',
    relatedPeople: [
      {
        nameJa: 'ローラ・マルヴィ',
        nameEn: 'Laura Mulvey',
        roleJa: '批評家',
        roleEn: 'Critic',
        urlEn: 'https://en.wikipedia.org/wiki/Laura_Mulvey'
      }
    ]
  },
  araki: {
    descriptorJa: '私写真',
    descriptorEn: 'Personal Photography',
    keywordsJa: '私写真、センチメンタルな旅、東京',
    keywordsEn: 'personal photography, Sentimental Journey, and Tokyo',
    representativeWorkJa: '『センチメンタルな旅』',
    representativeWorkEn: 'Sentimental Journey',
    relatedPeople: [
      {
        nameJa: '荒木陽子',
        nameEn: 'Yoko Araki',
        roleJa: '被写体・協働者',
        roleEn: 'Subject / Collaborator',
        urlEn: 'https://en.wikipedia.org/wiki/Nobuyoshi_Araki'
      }
    ]
  },
  salgado: {
    descriptorJa: '人道写真',
    descriptorEn: 'Humanist Documentary',
    keywordsJa: '労働、移民、地球規模のドキュメンタリー',
    keywordsEn: 'labor, migration, and global documentary photography',
    representativeWorkJa: '『Workers』',
    representativeWorkEn: 'Workers',
    relatedPeople: [
      {
        nameJa: 'レリア・サルガド',
        nameEn: 'Lelia Wanick Salgado',
        roleJa: '編集者',
        roleEn: 'Editor',
        urlEn: 'https://en.wikipedia.org/wiki/Sebasti%C3%A3o_Salgado'
      }
    ]
  }
};

if (typeof window !== 'undefined') {
  window.PHOTOGRAPHER_ENRICHMENTS = PHOTOGRAPHER_ENRICHMENTS;
}
