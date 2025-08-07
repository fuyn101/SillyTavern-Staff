import { reactive, ref, toRaw } from 'vue';
import { defineStore } from 'pinia';
import defaultJson from '@/assets/default_character.json';
import defaultPrompts from '@/assets/Default prompt.json';
import { getPreset, setPreset } from '@/utils/db';

// 完整的角色JSON数据结构
export interface CharacterData {
  avatar_data_url?: string;
  name: string;
  description: string;
  personality: string;
  scenario: string;
  first_mes: string;
  mes_example: string;
  creatorcomment: string;
  avatar: string;
  chat: string;
  talkativeness: string;
  fav: boolean;
  tags: string[];
  spec: string;
  spec_version: string;
  data: {
    name: string;
    description: string;
    personality: string;
    scenario: string;
    first_mes: string;
    mes_example: string;
    creator_notes: string;
    system_prompt: string;
    post_history_instructions: string;
    tags: string[];
    creator: string;
    character_version: string;
    alternate_greetings: string[];
    extensions: {
      talkativeness: string;
      fav: boolean;
      world: string;
      depth_prompt: {
        prompt: string;
        depth: number;
        role: string;
      };
      regex_scripts: Array<{
        id: string;
        scriptName: string;
        findRegex: string;
        replaceString: string;
        trimStrings: string[];
        placement: number[];
        disabled: boolean;
        markdownOnly: boolean;
        promptOnly: boolean;
        runOnEdit: boolean;
        substituteRegex: number;
        minDepth: number | null;
        maxDepth: number | null;
      }>;
    };
    group_only_greetings: string[];
    character_book: {
      entries: Array<{
        id: number;
        keys: string[];
        secondary_keys: string[];
        comment: string;
        content: string;
        constant: boolean;
        selective: boolean;
        insertion_order: number;
        enabled: boolean;
        position: string;
        use_regex: boolean;
        extensions: {
          position: number;
          exclude_recursion: boolean;
          display_index: number;
          probability: number;
          useProbability: boolean;
          depth: number;
          selectiveLogic: number;
          group: string;
          group_override: boolean;
          group_weight: number;
          prevent_recursion: boolean;
          delay_until_recursion: boolean;
          scan_depth: number | null;
          match_whole_words: number | null;
          use_group_scoring: boolean;
          case_sensitive: number | null;
          automation_id: string;
          role: number;
          vectorized: boolean;
          sticky: number;
          cooldown: number;
          delay: number;
        };
      }>;
      name: string;
    };
  };
  create_date: string;
}

export const useDataManager = defineStore('dataManager', () => {
  // State
  const editorCard = reactive<CharacterData>(
    JSON.parse(localStorage.getItem('editor_card') || JSON.stringify(defaultJson))
  );
  const originalData = reactive<CharacterData>(JSON.parse(JSON.stringify(editorCard)));
  const prompts = ref<any[]>(defaultPrompts.prompts);

  const presetEditorLeft = reactive<any>({ prompts: [] });
  const presetEditorRight = reactive<any>({ prompts: [] });
  const presetsReady = ref(false);

  // Actions
  const updatePrompts = (newPrompts: any[]) => {
    prompts.value = newPrompts;
  };


  const getEditorCard = (): CharacterData => {
    return JSON.parse(JSON.stringify(editorCard));
  };

  const setEditorCard = (data: CharacterData) => {
    Object.assign(editorCard, data);
    Object.assign(originalData, data);
    localStorage.setItem('editor_card', JSON.stringify(data));
  };

  const loadCardToEditor = (jsonString: string) => {
    try {
      const data = JSON.parse(jsonString);
      setEditorCard(data as CharacterData);
      return true;
    } catch (error) {
      console.error('JSON解析失败:', error);
      return false;
    }
  };

  const exportEditorCard = (): string => {
    return JSON.stringify(editorCard, null, 2);
  };

  const initPresets = async () => {
    const [leftData, rightData] = await Promise.all([getPreset('left'), getPreset('right')]);
    Object.assign(presetEditorLeft, leftData || { prompts: [] });
    Object.assign(presetEditorRight, rightData || { prompts: [] });
    presetsReady.value = true;
  };

  initPresets();

  const updatePresetEditorData = async (side: 'left' | 'right', data: any) => {
    const target = side === 'left' ? presetEditorLeft : presetEditorRight;
    Object.assign(target, data);
    try {
      await setPreset(side, toRaw(target));
    } catch (error) {
      console.error(`Failed to save preset to IndexedDB for side '${side}':`, error);
    }
  };

  const loadPresetToEditor = (presetData: any, side: 'left' | 'right') => {
    updatePresetEditorData(side, presetData);
  };

  // --- Character Card List Management ---
  const getCardList = (): CharacterData[] => {
    const list = localStorage.getItem('character_card_list');
    return list ? JSON.parse(list) : [];
  };

  const saveCardToList = (card: CharacterData) => {
    const list = getCardList();
    const existingIndex = list.findIndex(c => c.name === card.name);
    if (existingIndex > -1) {
      list[existingIndex] = card;
    } else {
      list.push(card);
    }
    localStorage.setItem('character_card_list', JSON.stringify(list));
  };

  const loadCardFromList = (name: string): boolean => {
    const list = getCardList();
    const card = list.find(c => c.name === name);
    if (card) {
      setEditorCard(card);
      return true;
    }
    return false;
  };

  const deleteCardFromList = (name: string) => {
    let list = getCardList();
    list = list.filter(c => c.name !== name);
    localStorage.setItem('character_card_list', JSON.stringify(list));
  };
  
  const getCardsByNames = (names: string[]): CharacterData[] => {
    const list = getCardList();
    return list.filter(c => names.includes(c.name));
  };

  const deleteCardsFromList = (names: string[]) => {
    let list = getCardList();
    list = list.filter(c => !names.includes(c.name));
    localStorage.setItem('character_card_list', JSON.stringify(list));
  };

  const clearAllCards = () => {
    localStorage.setItem('character_card_list', JSON.stringify([]));
  };

  // --- Preset List Management ---
  const getPresetList = (): any[] => {
    const list = localStorage.getItem('preset_list');
    return list ? JSON.parse(list) : [];
  };

  const savePresetToList = (preset: any, name: string) => {
    const list = getPresetList();
    const existingIndex = list.findIndex(p => p.name === name);
    const presetWithName = { ...preset, name };
    if (existingIndex > -1) {
      list[existingIndex] = presetWithName;
    } else {
      list.push(presetWithName);
    }
    localStorage.setItem('preset_list', JSON.stringify(list));
  };

  const loadPresetFromList = (name: string): any | null => {
    const list = getPresetList();
    return list.find(p => p.name === name) || null;
  };

  const deletePresetFromList = (name: string) => {
    let list = getPresetList();
    list = list.filter(p => p.name !== name);
    localStorage.setItem('preset_list', JSON.stringify(list));
  };

  return {
    editorCard,
    prompts,
    presetEditorLeft,
    presetEditorRight,
    presetsReady,
    updatePrompts,
    getEditorCard,
    setEditorCard,
    loadCardToEditor,
    exportEditorCard,
    updatePresetEditorData,
    loadPresetToEditor,
    // Card List
    getCardList,
    saveCardToList,
    loadCardFromList,
    deleteCardFromList,
    getCardsByNames,
    deleteCardsFromList,
    clearAllCards,
    // Preset List
    getPresetList,
    savePresetToList,
    loadPresetFromList,
    deletePresetFromList,
  };
});
