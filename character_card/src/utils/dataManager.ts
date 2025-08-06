import { reactive } from 'vue'
import defaultJson from './default.json'

// 完整的林凰JSON数据结构
export interface CharacterData {
  name: string
  description: string
  personality: string
  scenario: string
  first_mes: string
  mes_example: string
  creatorcomment: string
  avatar: string
  chat: string
  talkativeness: string
  fav: boolean
  tags: string[]
  spec: string
  spec_version: string
  data: {
    name: string
    description: string
    personality: string
    scenario: string
    first_mes: string
    mes_example: string
    creator_notes: string
    system_prompt: string
    post_history_instructions: string
    tags: string[]
    creator: string
    character_version: string
    alternate_greetings: string[]
    extensions: {
      talkativeness: string
      fav: boolean
      world: string
      depth_prompt: {
        prompt: string
        depth: number
        role: string
      }
      regex_scripts: Array<{
        id: string
        scriptName: string
        findRegex: string
        replaceString: string
        trimStrings: string[]
        placement: number[]
        disabled: boolean
        markdownOnly: boolean
        promptOnly: boolean
        runOnEdit: boolean
        substituteRegex: number
        minDepth: number | null
        maxDepth: number | null
      }>
    }
    group_only_greetings: string[]
    character_book: {
      entries: Array<{
        id: number
        keys: string[]
        secondary_keys: string[]
        comment: string
        content: string
        constant: boolean
        selective: boolean
        insertion_order: number
        enabled: boolean
        position: string
        use_regex: boolean
        extensions: {
          position: number
          exclude_recursion: boolean
          display_index: number
          probability: number
          useProbability: boolean
          depth: number
          selectiveLogic: number
          group: string
          group_override: boolean
          group_weight: number
          prevent_recursion: boolean
          delay_until_recursion: boolean
          scan_depth: number | null
          match_whole_words: number | null
          use_group_scoring: boolean
          case_sensitive: number | null
          automation_id: string
          role: number
          vectorized: boolean
          sticky: number
          cooldown: number
          delay: number
        }
      }>
      name: string
    }
  }
  create_date: string
}

// 默认数据
const defaultData: CharacterData = defaultJson as CharacterData

// 响应式数据存储
const CharData = reactive<CharacterData>(JSON.parse(JSON.stringify(defaultData)))
const originalData = reactive<CharacterData>(JSON.parse(JSON.stringify(defaultData)))

// 数据管理器
export const useDataManager = () => {
  // 获取完整数据
  const getFullData = (): CharacterData => {
    return JSON.parse(JSON.stringify(CharData))
  }

  // 获取基础数据（顶层字段）
  const getBasicData = () => {
    // 直接返回 CharData 的引用，而不是解构
    // 这样组件可以直接修改原始数据
    return CharData
  }

  // 获取数据字段内容
  const getDataField = () => {
    return CharData.data
  }

  // 设置完整数据
  const setFullData = (data: CharacterData) => {
    Object.assign(CharData, data)
    Object.assign(originalData, data)
  }

  // 设置基础数据
  const setBasicData = (basicData: Partial<CharacterData>) => {
    Object.assign(CharData, basicData)
  }

  // 设置数据字段内容
  const setDataField = (dataField: Partial<CharacterData['data']>) => {
    Object.assign(CharData.data, dataField)
  }

  // 重置数据
  const resetData = () => {
    Object.assign(CharData, originalData)
  }

  // 重置为默认数据
  const resetToDefault = () => {
    Object.assign(CharData, defaultData)
    Object.assign(originalData, defaultData)
  }

  // 从JSON字符串加载数据
  const loadFromJson = (jsonString: string) => {
    try {
      const data = JSON.parse(jsonString)
      setFullData(data as CharacterData)
      return true
    } catch (error) {
      console.error('JSON解析失败:', error)
      return false
    }
  }

  // 导出为JSON字符串
  const exportToJson = (): string => {
    // 创建数据的深拷贝以避免修改原始数据
    const dataCopy = JSON.parse(JSON.stringify(CharData))
    return JSON.stringify(dataCopy, null, 2)
  }

  // 验证基础数据
  const validateBasicData = (): { valid: boolean; errors: string[] } => {
    const errors: string[] = []

    if (!CharData.name) errors.push('角色名称不能为空')
    if (!CharData.description) errors.push('描述不能为空')

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  // 验证数据字段
  const validateDataField = (): { valid: boolean; errors: string[] } => {
    const errors: string[] = []

    if (!CharData.data.name) errors.push('数据名称不能为空')
    if (!CharData.data.description) errors.push('数据描述不能为空')

    return {
      valid: errors.length === 0,
      errors,
    }
  }

  // 验证完整数据
  const validateData = (): { valid: boolean; errors: string[] } => {
    const basicValidation = validateBasicData()
    const dataFieldValidation = validateDataField()

    const allErrors = [...basicValidation.errors, ...dataFieldValidation.errors]

    return {
      valid: allErrors.length === 0,
      errors: allErrors,
    }
  }

  // 保存数据到本地存储
  const saveToLocalStorage = (): { success: boolean; message: string } => {
    try {
      const validation = validateData()
      if (!validation.valid) {
        return {
          success: false,
          message: '验证失败：' + validation.errors.join('；'),
        }
      }

      localStorage.setItem('linhuang_full_data', exportToJson())

      return {
        success: true,
        message: '数据保存成功！',
      }
    } catch (error) {
      return {
        success: false,
        message: '保存失败：' + (error as Error).message,
      }
    }
  }

  // 保存基础数据到本地存储
  const saveBasicDataToLocalStorage = (): { success: boolean; message: string } => {
    try {
      const validation = validateBasicData()
      if (!validation.valid) {
        return {
          success: false,
          message: '验证失败：' + validation.errors.join('；'),
        }
      }

      localStorage.setItem('linhuang_full_data', exportToJson())

      return {
        success: true,
        message: '基础数据保存成功！',
      }
    } catch (error) {
      return {
        success: false,
        message: '保存失败：' + (error as Error).message,
      }
    }
  }

  // 保存数据字段到本地存储
  const saveDataFieldToLocalStorage = (): { success: boolean; message: string } => {
    try {
      const validation = validateDataField()
      if (!validation.valid) {
        return {
          success: false,
          message: '验证失败：' + validation.errors.join('；'),
        }
      }

      localStorage.setItem('linhuang_full_data', exportToJson())

      return {
        success: true,
        message: 'Data 数据保存成功！',
      }
    } catch (error) {
      return {
        success: false,
        message: '保存失败：' + (error as Error).message,
      }
    }
  }

  return {
    linhuangData: CharData,
    getFullData,
    getBasicData,
    getDataField,
    setFullData,
    setBasicData,
    setDataField,
    resetData,
    resetToDefault,
    loadFromJson,
    exportToJson,
    validateData,
    validateBasicData,
    validateDataField,

    saveBasicDataToLocalStorage,
    saveDataFieldToLocalStorage,
  }
}
