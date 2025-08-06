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
  const characterData = reactive<CharacterData>(
    JSON.parse(localStorage.getItem('character_full_data') || JSON.stringify(defaultJson))
  );
  const originalData = reactive<CharacterData>(JSON.parse(JSON.stringify(characterData)));
  const prompts = ref<any[]>(defaultPrompts.prompts);

  const presetEditorLeft = reactive<any>({ prompts: [] });
  const presetEditorRight = reactive<any>({ prompts: [] });
  const presetsReady = ref(false);

  // Actions
  const updatePrompts = (newPrompts: any[]) => {
    prompts.value = newPrompts;
  };


  const getFullData = (): CharacterData => {
    return JSON.parse(JSON.stringify(characterData));
  };

  const setFullData = (data: CharacterData) => {
    Object.assign(characterData, data);
    Object.assign(originalData, data);
    localStorage.setItem('character_full_data', JSON.stringify(data));
  };

  const loadFromJson = (jsonString: string) => {
    try {
      const data = JSON.parse(jsonString);
      setFullData(data as CharacterData);
      return true;
    } catch (error) {
      console.error('JSON解析失败:', error);
      return false;
    }
  };

  const exportToJson = (): string => {
    return JSON.stringify(characterData, null, 2);
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

  return {
    characterData,
    prompts,
    presetEditorLeft,
    presetEditorRight,
    presetsReady,
    updatePrompts,
    getFullData,
    setFullData,
    loadFromJson,
    exportToJson,
    updatePresetEditorData,
    loadPresetToEditor,
  };
});
