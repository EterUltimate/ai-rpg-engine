# 游戏资源说明

## 目录结构

```
public/
├── assets/
│   ├── sprites/      # 角色和NPC精灵图
│   ├── maps/         # 地图数据文件
│   ├── tiles/        # 地图瓦片
│   ├── audio/        # 音效和背景音乐
│   └── fonts/        # 游戏字体
└── vite.svg          # 网站图标
```

## 资源要求

### 精灵图 (Sprites)
- **格式**: PNG (支持透明背景)
- **推荐大小**: 32x32, 64x64, 或 128x128 像素
- **命名规范**: 
  - `player.png` - 玩家角色
  - `npc_[name].png` - NPC角色
  - `enemy_[type].png` - 敌人

### 地图瓦片 (Tiles)
- **格式**: PNG
- **推荐大小**: 32x32 或 64x64 像素
- **命名规范**:
  - `ground.png` - 地面
  - `wall.png` - 墙壁
  - `water.png` - 水域

### 地图数据 (Maps)
- **格式**: JSON (Tiled Map Editor导出)
- **包含内容**:
  - 地图尺寸
  - 瓦片图层
  - 碰撞层
  - 对象层(NPC位置、事件触发器等)

## 资源来源

### 免费资源推荐
1. **OpenGameArt**: https://opengameart.org/
2. **itch.io**: https://itch.io/game-assets/free/tag-sprite
3. **Kenney Assets**: https://kenney.nl/assets

### 自定义资源
可使用以下工具创建:
- **Aseprite**: 像素画编辑器
- **Tiled**: 地图编辑器
- **Piskel**: 免费在线像素画编辑器

## 示例资源

项目当前使用占位符,需要替换为实际游戏资源。

### 最小可行产品(MVP)需要:
1. 玩家角色精灵 (4方向行走动画)
2. 基础地形瓦片 (草地、石头、水)
3. 至少1个NPC精灵
4. 背景音乐 (可选)
5. 音效 (可选)

## 资源加载

前端游戏引擎会自动从 `/public/assets/` 目录加载资源。

确保在 `MainScene.tsx` 中正确配置资源路径:
```typescript
this.load.image('player', '/assets/sprites/player.png');
this.load.image('ground', '/assets/tiles/ground.png');
```
