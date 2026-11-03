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
(1, '荧光定量 PCR 仪',     'ABI QuantStudio 5',  4, 3),
(1, '全自动核酸提取仪',     'KingFisher Flex',    2, 2),
(2, 'II 级生物安全柜',      'BSC-1500IIA2',       2, 2),
(2, '恒温培养箱',           'SPX-250',            6, 5),
(3, '高效液相色谱仪',       'Agilent 1260',       3, 2),
(3, '气相色谱-质谱联用仪',  'GCMS-QP2020',        1, 1),
(4, '化学发光免疫分析仪',   'CL-6000i',           2, 2),
(4, '酶标仪',               'Multiskan FC',       4, 4),
(5, '低温离心机',           'Centrifuge 5810R',   2, 0),
(5, '样本分装台',           '生物安全型',          4, 0);