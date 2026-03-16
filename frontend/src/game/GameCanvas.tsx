import { useEffect, useRef } from 'react'
import Phaser from 'phaser'
import MainScene from './scenes/MainScene'
import useGameStore from '../store/gameStore'

const GameCanvas: React.FC = () => {
  const gameRef = useRef<Phaser.Game | null>(null)
  const setPhaserGame = useGameStore(state => state.setPhaserGame)

  useEffect(() => {
    if (gameRef.current) return

    const config: Phaser.Types.Core.GameConfig = {
      type: Phaser.AUTO,
      width: window.innerWidth,
      height: window.innerHeight,
      parent: 'phaser-game',
      backgroundColor: '#1e1b4b',
      physics: {
        default: 'arcade',
        arcade: {
          gravity: { x: 0, y: 0 },
          debug: false,
        },
      },
      scene: [MainScene],
      scale: {
        mode: Phaser.Scale.RESIZE,
        autoCenter: Phaser.Scale.CENTER_BOTH,
      },
      render: {
        pixelArt: true,
        antialias: false,
      },
    }

    gameRef.current = new Phaser.Game(config)
    setPhaserGame(gameRef.current)

    // 响应窗口大小变化
    const handleResize = () => {
      if (gameRef.current) {
        gameRef.current.scale.resize(window.innerWidth, window.innerHeight)
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      if (gameRef.current) {
        gameRef.current.destroy(true)
        gameRef.current = null
      }
    }
  }, [setPhaserGame])

  return <div id="phaser-game" className="absolute inset-0" />
}

export default GameCanvas
