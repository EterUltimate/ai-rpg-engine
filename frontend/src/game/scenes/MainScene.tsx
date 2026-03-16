import Phaser from 'phaser'
import { Player } from '../entities/Player'
import useGameStore from '../../store/gameStore'

export default class MainScene extends Phaser.Scene {
  private player!: Player
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys

  constructor() {
    super({ key: 'MainScene' })
  }

  preload() {
    // 加载游戏资源
    this.load.image('player', '/assets/sprites/player.png')
    this.load.image('ground', '/assets/tiles/ground.png')
    this.load.image('npc', '/assets/sprites/npc.png')
    
    // 加载地图tileset (如果有)
    // this.load.tilemapTiledJSON('map', '/assets/maps/world.json')
  }

  create() {
    // 创建简单的地面
    const ground = this.add.rectangle(
      this.scale.width / 2,
      this.scale.height - 50,
      this.scale.width,
      100,
      0x4a5568
    )
    this.physics.add.existing(ground, true)

    // 创建玩家
    this.player = new Player(
      this,
      this.scale.width / 2,
      this.scale.height - 150,
      'player'
    )

    // 设置碰撞
    this.physics.add.collider(this.player, ground)

    // 创建NPC
    const npc = this.add.rectangle(
      this.scale.width / 2 + 200,
      this.scale.height - 150,
      40,
      60,
      0x9333ea
    )
    this.physics.add.existing(npc, true)
    npc.setData('type', 'npc')
    npc.setData('name', '神秘老人')

    // NPC交互
    this.physics.add.overlap(
      this.player,
      npc,
      this.handleNPCInteraction as Phaser.Types.Physics.Arcade.ArcadePhysicsCallback,
      undefined,
      this
    )

    // 设置键盘控制
    if (this.input.keyboard) {
      this.cursors = this.input.keyboard.createCursorKeys()
    }

    // 添加游戏状态文本
    this.add.text(20, 20, 'AI-RPG Engine', {
      fontSize: '24px',
      color: '#f3f4f6',
    })

    this.add.text(20, 50, '按空格键打开AI对话', {
      fontSize: '16px',
      color: '#9ca3af',
    })
  }

  update() {
    if (this.player && this.cursors) {
      this.player.update(this.cursors)
    }
  }

  private handleNPCInteraction(
    _player: Phaser.GameObjects.GameObject,
    npc: Phaser.GameObjects.GameObject
  ) {
    const store = useGameStore.getState()
    
    // 打开聊天界面
    store.toggleChat()
    
    // 设置NPC信息
    const npcName = npc.getData('name') || 'NPC'
    console.log(`与 ${npcName} 交互`)
  }
}
