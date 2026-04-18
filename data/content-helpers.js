function createEraStub({ id, period, title, titleEn = '', worldEvents = {}, photoContext = {} }) {
  return {
    id,
    period,
    title,
    titleEn,
    worldEvents: {
      text: worldEvents.text || '',
      textEn: worldEvents.textEn || '',
      sources: worldEvents.sources || [],
    },
    photoContext: {
      text: photoContext.text || '',
      textEn: photoContext.textEn || '',
      sources: photoContext.sources || [],
    },
  };
}

function createPhotographerStub({ id, era, label }) {
  return {
    id,
    name: '',
    nameJa: label || '追加予定',
    nationality: '',
    flag: '',
    years: '',
    gender: '',
    era,
    movements: [],
    thumbnail: '',
    links: [],
    amazon: '',
    isPlaceholder: true,
    context: {
      text: '',
      citations: [],
    },
  };
}
