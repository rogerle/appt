import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      
      // PWA 基础配置 (Apple Design System)
      includeAssets: ['favicon.ico', 'robots.txt', 'icons/*.svg'],
      
      // manifest.json 配置 - Apple Blue theme
      manifest: {
        name: 'Appt - Yoga Studio Scheduler',
        short_name: 'Appt',
        description: '瑜伽馆预约管理系统',
        theme_color: '#0071e3', // Apple Blue as per design system
        background_color: '#f5f5f7', // Light gray (not white) per Apple spec
        display: 'standalone',
        orientation: 'portrait-primary',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/icons/icon-192x192.svg',
            sizes: '192x192',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          },
          {
            src: '/icons/icon-512x512.svg',
            sizes: '512x512',
            type: 'image/svg+xml',
            purpose: 'any maskable'
          }
        ],
        shortcuts: [
          {
            name: '预约课程',
            url: '/booking',
            description: '开始预约瑜伽课程'
          },
          {
            name: '我的预约',
            url: '/my-bookings',
            description: '查看我的预约记录'
          }
        ]
      },

      // Service Worker 配置
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,png,ico}'],
        
        // 离线缓存策略
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\..*$/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 // 24 hours
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'image-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 30 // 30 days
              }
            }
          }
        ]
      },

      // 开发者选项
      devOptions: {
        enabled: true,
        navigateFallback: '/index.html',
        type: 'module'
      }
    })
  ],

  // 环境变量配置
  envPrefix: 'VITE_',

  // 代理配置（开发环境）
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },

  // 构建优化
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          tailwind: ['./src/styles/main.css']
        }
      }
    }
  },

  // CSS 配置
  css: {
    postcss: './postcss.config.js'
  }
})
