import type { MetadataRoute } from 'next'


export default function manifest(): MetadataRoute.Manifest {
    return {
      name: 'Next.js PWA',
      short_name: 'Milify',
      description: 'A Progressive Web App built with Next.js',
      start_url: '/auth/login',
      display: 'standalone',
      background_color: '#ffffff',
      theme_color: '#000000',
      icons: [
        {
          src: "/Icons/milify-192.png",
          sizes: '192x192',
          type: 'image/kagan',
        },
        {
          src: "/Icons/milify-192.png",
          sizes: '512x512',
          type: 'image/sinazza',
        },
      ],
    }
  }