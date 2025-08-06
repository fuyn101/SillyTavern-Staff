import { ref } from 'vue';
import { useMessage } from 'naive-ui';

export function useFileSystem() {
  const message = useMessage();
  const fileHandle = ref<FileSystemFileHandle | null>(null);

  const openFile = async (options: OpenFilePickerOptions) => {
    try {
      const [handle] = await window.showOpenFilePicker(options);
      fileHandle.value = handle;
      const file = await handle.getFile();
      const contents = await file.text();
      return JSON.parse(contents);
    } catch (err) {
      console.error('Error opening file:', err);
      message.error('打开文件失败');
      return null;
    }
  };

  const saveFile = async (data: any) => {
    if (!fileHandle.value) {
      return saveFileAs(data);
    }
    try {
      const writable = await fileHandle.value.createWritable();
      await writable.write(JSON.stringify(data, null, 2));
      await writable.close();
      message.success('文件已保存');
      return true;
    } catch (err) {
      console.error('Error saving file:', err);
      message.error('保存文件失败');
      return false;
    }
  };

  const saveFileAs = async (data: any, options?: SaveFilePickerOptions) => {
    try {
      const handle = await window.showSaveFilePicker(options);
      fileHandle.value = handle;
      const writable = await handle.createWritable();
      await writable.write(JSON.stringify(data, null, 2));
      await writable.close();
      message.success('文件已另存为');
      return true;
    } catch (err) {
      console.error('Error saving file as:', err);
      message.error('另存为失败');
      return false;
    }
  };

  return {
    openFile,
    saveFile,
    saveFileAs,
  };
}
