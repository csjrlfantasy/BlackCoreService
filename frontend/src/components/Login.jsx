import React, { useState } from 'react';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { Button, Form, Input, message } from 'antd';
import axios from '../utils/axiosConfig'; // 改用配置好的axios实例
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const onFinish = async (values) => {
    setLoading(true);
    try {
      // 修改请求地址为相对路径
      const response = await axios.post('/user_services/login', {
        username: values.username,
        password: values.password
      });

      // 修改点1：增加更严格的成功条件判断
      if (response.status === 200 && response.data.token) {
        localStorage.setItem('authToken', response.data.token);
        message.success('登录成功');
        
        // 修改点2：添加导航前的延时确保状态更新
        setTimeout(() => {
          navigate('/dashboard', { replace: true }); // 使用replace模式防止回退
        }, 6);
      }
    } catch (error) {
      // 修改点3：增强错误日志
      console.error('登录请求失败:', error);
      message.error(error.response?.data?.message || '登录服务不可用');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div 
      className="login-container" 
      style={{ 
        maxWidth: 400,
        margin: '100px auto',
        padding: 24,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        borderRadius: 8
      }}
    >
      <h2 data-cy="login-title" style={{ textAlign: 'center', marginBottom: 24 }}>
        用户登录
      </h2>
      <Form
        name="login"
        initialValues={{ remember: true }}
        onFinish={onFinish}
        data-cy="login-form"
      >
        <Form.Item
          name="username"
          rules={[{ required: true, message: '请输入用户名!' }]}
        >
          <Input 
            prefix={<UserOutlined />} 
            placeholder="用户名" 
            data-cy="username-input"
          />
        </Form.Item>

        <Form.Item
          name="password"
          rules={[{ required: true, message: '请输入密码!' }]}
        >
          <Input.Password
            prefix={<LockOutlined />}
            placeholder="密码"
            data-cy="password-input"
          />
        </Form.Item>

        <Form.Item>
          <Button 
            type="primary" 
            htmlType="submit" 
            loading={loading}
            block
            data-cy="submit-button"
          >
            登录
          </Button>
        </Form.Item>

        <Form.Item style={{ textAlign: 'center', marginTop: 24 }}>
          <Button 
            type="link" 
            onClick={() => navigate('/')}
            data-cy="home-link"
          >
            返回首页
          </Button>
        </Form.Item>

        <Form.Item style={{ textAlign: 'center', marginBottom: 0 }}>
          <Button 
            type="link" 
            onClick={() => navigate('/register')}
            data-cy="register-button"
          >
            没有账号？立即注册
          </Button>
        </Form.Item>
      </Form> {/* 只保留一个闭合标签 */}
    </div>
  );
};

export default Login;