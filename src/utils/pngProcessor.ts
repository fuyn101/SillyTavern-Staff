const crc32 = (function() {
    const table = new Uint32Array(256);
    for (let i = 0; i < 256; i++) {
        let c = i;
        for (let k = 0; k < 8; k++) {
            c = (c & 1) ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
        }
        table[i] = c;
    }
    return function(bytes: Uint8Array): number {
        let crc = 0xFFFFFFFF;
        for (let i = 0; i < bytes.length; i++) {
            crc = table[(crc ^ bytes[i]) & 0xFF] ^ (crc >>> 8);
        }
        return (crc ^ 0xFFFFFFFF) >>> 0;
    };
})();

export const extractDataFromPng = (arrayBuffer: ArrayBuffer): object | null => {
  const view = new DataView(arrayBuffer);
  if (view.getUint32(0) !== 0x89504e47 || view.getUint32(4) !== 0x0d0a1a0a) {
    throw new Error('不是有效的PNG文件。');
  }

  let offset = 8;
  while (offset < view.byteLength) {
    const length = view.getUint32(offset);
    const type = String.fromCharCode(
      view.getUint8(offset + 4),
      view.getUint8(offset + 5),
      view.getUint8(offset + 6),
      view.getUint8(offset + 7)
    );

    if (type === 'tEXt') {
      const chunkDataOffset = offset + 8;
      const chunkData = new Uint8Array(arrayBuffer, chunkDataOffset, length);
      
      let nullIndex = -1;
      for (let i = 0; i < chunkData.length; i++) {
          if (chunkData[i] === 0) {
              nullIndex = i;
              break;
          }
      }

      if (nullIndex !== -1) {
          const keyDecoder = new TextDecoder('ascii');
          const key = keyDecoder.decode(chunkData.subarray(0, nullIndex));

          if (key === 'ccv3') {
              const base64Data = keyDecoder.decode(chunkData.subarray(nullIndex + 1));
              const binaryString = atob(base64Data);
              const bytes = new Uint8Array(binaryString.length);
              for (let i = 0; i < binaryString.length; i++) {
                  bytes[i] = binaryString.charCodeAt(i);
              }
              
              const utf8Decoder = new TextDecoder('utf-8');
              const jsonString = utf8Decoder.decode(bytes);
              
              return JSON.parse(jsonString);
          }
      }
    }

    offset += 12 + length;
  }

  return null;
};

export const embedDataInPng = (card: any, imageDataUrl: string): Promise<Blob> => {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext('2d');
      if (!ctx) {
        return reject(new Error('无法获取Canvas上下文'));
      }
      ctx.drawImage(img, 0, 0);

      const dataUrl = canvas.toDataURL('image/png');
      
      const cardDataToEmbed = { ...card };
      delete cardDataToEmbed.avatar_data_url;
      const jsonString = JSON.stringify(cardDataToEmbed);
      
      const base64Png = dataUrl.split(',')[1];
      const binaryPng = atob(base64Png);
      const arrayBuffer = new ArrayBuffer(binaryPng.length);
      const uint8Array = new Uint8Array(arrayBuffer);
      for (let i = 0; i < binaryPng.length; i++) {
        uint8Array[i] = binaryPng.charCodeAt(i);
      }

      const dataView = new DataView(uint8Array.buffer);
      let offset = 8;
      let iendOffset = -1;

      while (offset < dataView.byteLength) {
        const length = dataView.getUint32(offset);
        const type = String.fromCharCode(
          dataView.getUint8(offset + 4),
          dataView.getUint8(offset + 5),
          dataView.getUint8(offset + 6),
          dataView.getUint8(offset + 7)
        );
        if (type === 'IEND') {
          iendOffset = offset;
          break;
        }
        offset += 12 + length;
      }

      if (iendOffset === -1) {
        return reject(new Error('无法找到PNG的IEND块'));
      }

      const textEncoder = new TextEncoder();
      const key = 'ccv3';
      const value = btoa(unescape(encodeURIComponent(jsonString)));
      const textChunkData = textEncoder.encode(key + '\0' + value);
      
      const chunkTypeAndData = new Uint8Array(4 + textChunkData.length);
      chunkTypeAndData.set(textEncoder.encode('tEXt'), 0);
      chunkTypeAndData.set(textChunkData, 4);
      
      const crc = crc32(chunkTypeAndData);

      const textChunk = new Uint8Array(12 + textChunkData.length);
      const textChunkView = new DataView(textChunk.buffer);

      textChunkView.setUint32(0, textChunkData.length);
      textChunk.set(chunkTypeAndData, 4);
      textChunkView.setUint32(8 + textChunkData.length, crc);

      const newPngData = new Uint8Array(uint8Array.length + textChunk.length);
      newPngData.set(uint8Array.subarray(0, iendOffset));
      newPngData.set(textChunk, iendOffset);
      newPngData.set(uint8Array.subarray(iendOffset), iendOffset + textChunk.length);

      resolve(new Blob([newPngData], { type: 'image/png' }));
    };
    img.onerror = () => {
      reject(new Error('无法加载角色头像图片。'));
    };
    img.src = imageDataUrl;
  });
};
