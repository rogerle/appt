// 自动生成 PWA 图标脚本
// 运行：node generate-icons.js

const fs = require('fs');
const path = require('path');

const sizes = [192, 512]; // PWA 需要的标准尺寸

sizes.forEach(size => {
  const canvasSize = size;
  
  // 创建 Canvas
  const canvas = document.createElement('canvas');
  canvas.width = canvasSize;
  canvas.height = canvasSize;
  const ctx = canvas.getContext('2d');

  // 背景渐变 (teal to blue)
  const gradient = ctx.createLinearGradient(0, 0, canvasSize, canvasSize);
  gradient.addColorStop(0, '#14b8a6'); // teal-500
  gradient.addColorStop(1, '#3b82f6'); // blue-500
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvasSize, canvasSize);

  // 绘制瑜伽图标 (简化的莲花图案)
  ctx.fillStyle = 'white';
  
  const centerX = canvasSize / 2;
  const centerY = canvasSize / 2;
  const radius = canvasSize * 0.3;

  // 绘制花瓣
  for (let i = 0; i < 8; i++) {
    ctx.beginPath();
    const angle = (i * Math.PI) / 4;
    const x = centerX + Math.cos(angle) * radius * 0.5;
    const y = centerY + Math.sin(angle) * radius * 0.5;
    
    ctx.ellipse(x, y, radius * 0.3, radius * 0.5, angle, 0, Math.PI * 2);
    ctx.fill();
  }

  // 保存图标
  canvas.toBlob(blob => {
    const file = new File([blob], `icon-${size}x${size}.png`, { type: 'image/png' });
    console.log(`Generated icon-${size}x${size}.png`);
  }, 'image/png');
});

console.log('Icon generation complete!');
