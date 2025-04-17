import React from 'react';
import { useNavigate } from 'react-router-dom';

const familyData = [
  {
    id: 0,
    name: '👴 爷爷',
    children: [
      {
        id: 1,
        name: '👦 大儿子',
        children: [
          { id: 3, name: '👶 大孙子' },
          { id: 4, name: '👶 二孙子' }
        ]
      },
      { id: 2, name: '👦 二儿子' },
      { id: 5, name: '👦 三儿子' }
    ]
  }
];

const FamilyMember = ({ member, level = 0 }) => {
  const navigate = useNavigate();
  
  const handleNavigate = () => {
    // 跳转到成员详情页，示例路径需要与路由配置匹配
    navigate(`/member/${member.id}`);
  };

  return (
    <div style={{ 
      marginLeft: level * 30,
      padding: 10,
      borderLeft: level > 0 ? '2px solid #69c0ff' : 'none',
      position: 'relative',
      cursor: 'pointer' // 添加可点击手势
    }}>
      <div 
        style={{ 
          fontWeight: level === 0 ? 'bold' : 'normal',
          fontSize: 16 + (2 - level) * 2,
          color: level === 0 ? '#ff4d4f' : '#1890ff',
          textDecoration: 'underline' // 添加下划线效果
        }}
        onClick={handleNavigate}
      >
        {member.name}
      </div>
      
      {/* 保持子节点渲染逻辑不变 */}
      {member.children?.map(child => (
        <FamilyMember key={child.id} member={child} level={level + 1} />
      ))}
    </div>
  );
};

// 新增导航按钮组件
const NavigationPanel = () => {
  const navigate = useNavigate();
  
  return (
    <div style={{
      display: 'flex',
      gap: 10,
      marginBottom: 20,
      justifyContent: 'center'
    }}>
      <Button type="primary" onClick={() => navigate('/family')}>
        家族树
      </Button>
      <Button onClick={() => navigate('/members')}>
        成员列表
      </Button>
      <Button onClick={() => navigate('/settings')}>
        设置
      </Button>
    </div>
  );
};

// 修改主组件
const FamilyTree = () => {
  return (
    <div style={{ 
      padding: 20,
      border: '1px solid #d9d9d9',
      borderRadius: 8,
      maxWidth: 600,
      margin: '20px auto'
    }}>
      <NavigationPanel />
      {familyData.map(member => (
        <FamilyMember key={member.id} member={member} />
      ))}
    </div>
  );
};

export default FamilyTree;