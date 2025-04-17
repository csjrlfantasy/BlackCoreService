import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Tag, Collapse, Table, Spin, Statistic, Button } from 'antd';
import { UserOutlined, ClockCircleOutlined, WalletOutlined } from '@ant-design/icons';
// 修改导入路径（从'../../utils'改为'../utils'）
import axios from '../utils/axiosConfig';

// 在文件底部添加默认导出
const Profile = () => {
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);

  // 修改axios实例配置（推荐在单独文件中配置，这里先做简单修改）
  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('authToken');
        if (!token) {
          message.error('请先登录');
          return;
        }

        // 修改请求部分
        const response = await axios.get('/user_services/user_info', {
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        if (response.data && response.data.user_id) {
          setUserData(response.data);
        } else {
          throw new Error('无效的用户数据');
        }
      } catch (error) {
        console.error('请求失败:', error);
        message.error(error.response?.data?.message || error.message || '服务不可用');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const orderColumns = [
    { title: '订单号', dataIndex: 'order_id' },
    { title: '商品', dataIndex: 'product_id' },
    { title: '金额', render: (_, record) => `¥${record.total_price.toFixed(2)}` },
    { title: '时间', dataIndex: 'created_at' },
    { title: '状态', render: (_, record) => <Tag color={record.status === '已完成' ? 'green' : 'orange'}>{record.status}</Tag> }
  ];

  return (
    <div style={{ padding: 24 }}>
      <Spin spinning={loading}>
        {userData && (
          <Card title="个人中心" bordered={false}>
            <Row gutter={16}>
              <Col span={8}>
                <Card className="profile-card">
                  <div style={{ textAlign: 'center' }}>
                    <img 
                      data-cy="user-avatar"
                      src={process.env.PUBLIC_URL + userData.avatar_url}
                      alt="用户头像" 
                      style={{ width: '100%' }}
                    />
                    <h2>{userData.nickname || '匿名用户'}</h2>
                    <p><UserOutlined /> ID: {userData.user_id}</p>
                  </div>
                </Card>
              </Col>
              
              <Col span={16}>
                <Card title="账户概览">
                  <Row gutter={16}>
                    <Col span={12}>
                      <Statistic 
                        title="账户余额" 
                        value={userData.balance} 
                        precision={2}
                        prefix="¥"
                        suffix={
                          <Button type="link" size="small">充值</Button>
                        }
                      />
                    </Col>
                    <Col span={12}>
                      <div style={{ marginBottom: 16 }}>
                        <div><ClockCircleOutlined /> 注册时间: {userData.created_at || '未知'}</div>
                        {/* 移除last_login显示 */}
                        <div><WalletOutlined /> 用户等级: {userData.user_level || '普通会员'}</div>
                      </div>
                    </Col>
                  </Row>
                </Card>

                <Collapse ghost style={{ marginTop: 24 }}>
                  <Collapse.Panel header="最近交易记录" key="1">
                    <Table
                      columns={orderColumns}
                      dataSource={[...userData.pending_orders, ...userData.completed_orders]}
                      pagination={{ pageSize: 5 }}
                      rowKey="order_id"
                    />
                  </Collapse.Panel>
                  <Collapse.Panel header="当前购物车" key="2">
                    {/* 购物车内容展示 */}
                  </Collapse.Panel>
                </Collapse>
              </Col>
            </Row>
          </Card>
        )}
      </Spin>
    </div>
  );
};

export default Profile; // 添加这行导出语句