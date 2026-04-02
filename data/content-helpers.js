function createEraStub({ id, period, title }) {
  return {
    id,
    period,
    title,
    worldEvents: {
      text: '',
      sources: [],
    },
    photoContext: {
      text: '',
      sources: [],
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
