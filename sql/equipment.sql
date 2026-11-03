CREATE TABLE IF NOT EXISTS equipment (
  id        BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  lab_id    BIGINT       NOT NULL                COMMENT '所属实验室',
  name      VARCHAR(100) NOT NULL                COMMENT '设备名',
  model     VARCHAR(100) NOT NULL DEFAULT ''     COMMENT '型号',
  total     INT          NOT NULL DEFAULT 1      COMMENT '总数',
  available INT          NOT NULL DEFAULT 1      COMMENT '当前可用数',
  PRIMARY KEY (id),
  KEY idx_equipment_lab (lab_id),              -- 按"实验室查设备"是最高频查询，建索引
  CONSTRAINT fk_equipment_lab FOREIGN KEY (lab_id)
    REFERENCES labs(id) ON DELETE CASCADE      -- 删实验室→设备跟着删（从属关系才敢 CASCADE）
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='设备表';

INSERT INTO equipment (lab_id, name, model, total, available) VALUES
(1, '深度学习工作站', 'RTX4090 / i9 / 128G', 8, 6),
(2, '六轴机械臂',     'UR5e',                2, 2),
(2, '移动机器人平台', 'TurtleBot4',          3, 3),
(3, 'GPU 服务器',     '4×A100',              2, 1),
(4, '开发工位',       '标准配置',             40, 40),
(5, '核心路由器',     'Cisco ISR4451',       4, 4);