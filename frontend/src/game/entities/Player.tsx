import Phaser from 'phaser'
import useGameStore from '../../store/gameStore'

export class Player extends Phaser.Physics.Arcade.Sprite {
  private speed: number = 200

  constructor(
    scene: Phaser.Scene,
    x: number,
    y: number,
    texture: string
  ) {
    super(scene, x, y, texture)

    // 添加到场景
    scene.add.existing(this)
    scene.physics.add.existing(this)

    // 设置物理属性
    this.setCollideWorldBounds(true)
    this.setBounce(0.2)
    
    // 设置显示大小
    this.setDisplaySize(40, 60)
    this.setTint(0x6366f1)

    // 禁用重力
    if (this.body && 'setGravity' in this.body) {
      (this.body as Phaser.Physics.Arcade.Body).setGravity(0)
    }
  }

  update(cursors: Phaser.Types.Input.Keyboard.CursorKeys) {
    if (!this.body) return

    // 水平移动
    if (cursors.left.isDown) {
      this.setVelocityX(-this.speed)
    } else if (cursors.right.isDown) {
      this.setVelocityX(this.speed)
    } else {
      this.setVelocityX(0)
    }

    // 垂直移动
    if (cursors.up.isDown) {
      this.setVelocityY(-this.speed)
    } else if (cursors.down.isDown) {
      this.setVelocityY(this.speed)
    } else {
      this.setVelocityY(0)
    }

    // 空格键打开聊天
    if (Phaser.Input.Keyboard.JustDown(cursors.space)) {
      const store = useGameStore.getState()
      store.toggleChat()
    }
  }
}
