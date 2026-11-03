CREATE TABLE IF NOT EXISTS reservations (
  id             BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键',
  user_id        BIGINT       NOT NULL                COMMENT '预约人',
  lab_id         BIGINT       NOT NULL                COMMENT '实验室',
  date           DATE         NOT NULL                COMMENT '预约日期',
  start_time     TIME         NOT NULL                COMMENT '开始时刻',
  end_time       TIME         NOT NULL                COMMENT '结束时刻',
  purpose        VARCHAR(200) NOT NULL                COMMENT '用途',
  status         VARCHAR(20)  NOT NULL DEFAULT 'pending' COMMENT 'pending/approved/rejected/cancelled',
  review_comment VARCHAR(200) NOT NULL DEFAULT ''     COMMENT '审核意见',
  created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (id),
  KEY idx_resv_user (user_id),
  KEY idx_resv_lab_date (lab_id, date),
  CONSTRAINT fk_resv_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_resv_lab  FOREIGN KEY (lab_id)  REFERENCES labs(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预约表';