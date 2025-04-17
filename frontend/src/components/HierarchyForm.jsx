import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

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

const RecursiveFormItems = ({ data, level = 0 }) => {
  return (
    <div style={{ marginLeft: level * 20 }}>
      {data.map((item, index) => (
        <div key={item.id} style={{ 
          margin: 8,
          padding: 16,
          border: '1px solid #ddd',
          borderRadius: 4
        }}>
          <div>层级 {level + 1}-{index + 1}</div>
          
          {/* 子节点 */}
          {item.children && (
            <RecursiveFormItems 
              data={item.children} 
              level={level + 1}
            />
          )}
        </div>
      ))}
    </div>
  );
};

// 初始数据结构
const initialData = [
  {
    id: 1,
    children: [
      { id: 2 },  // 子节点
      { 
        id: 3,
        children: [
          { id: 4 },  // 孙子节点
          { id: 5 }
        ]
      }
    ]
  }
];

const HierarchyForm = () => {
  const [selectedSon, setSelectedSon] = useState('大儿子');
  const [selectedGrandsons, setSelectedGrandsons] = useState([]);
  const [region, setRegion] = useState('cn');

  // 新增状态管理
  const [selectedOption, setSelectedOption] = useState('option1');
  const [checkedItems, setCheckedItems] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('cn');

  return (
    <div style={{ display: 'flex', gap: 40 }}>
      {/* 原始家族树结构保持不变... */}

      {/* 新增独立表单区块 */}
      <div 
        data-cy="form-section"
        style={{
          padding: 20,
          border: '2px solid #91d5ff',
          borderRadius: 8,
          minWidth: 300
        }}
      >
        {/* 单选按钮组 */}
        <div style={{ marginBottom: 20 }}>
          <h3>成员类型</h3>
          {['option1', 'option2', 'option3'].map(option => (
            <label 
              key={option}
              style={{ display: 'block', margin: '8px 0' }}
              data-cy={`radio-${option}`}
            >
              <input
                type="radio"
                name="memberType"
                value={option}
                checked={selectedOption === option}
                onChange={(e) => setSelectedOption(e.target.value)}
              />
              {{
                option1: '直系亲属',
                option2: '旁系亲属',
                option3: '其他关系'
              }[option]}
            </label>
          ))}
        </div>

        {/* 多选框组 */}
        <div style={{ marginBottom: 20 }}>
          <h3>特征选择</h3>
          {['trait1', 'trait2', 'trait3'].map(trait => (
            <label
              key={trait}
              style={{ display: 'block', margin: '8px 0' }}
              data-cy={`checkbox-${trait}`}
            >
              <input
                type="checkbox"
                value={trait}
                checked={checkedItems.includes(trait)}
                onChange={(e) => {
                  const newChecked = e.target.checked
                    ? [...checkedItems, trait]
                    : checkedItems.filter(item => item !== trait);
                  setCheckedItems(newChecked);
                }}
              />
              {{
                trait1: '共同居住',
                trait2: '经济关联',
                trait3: '法律关联'
              }[trait]}
            </label>
          ))}
        </div>

        {/* 下拉选择框 */}
        <div>
          <h3>地区选择</h3>
          <select
            data-cy="country-select"
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            style={{ width: '100%', padding: 8 }}
          >
            <option value="cn">中国</option>
            <option value="us">美国</option>
            <option value="uk">英国</option>
          </select>
        </div>
      </div>
    </div>
  );
};

export default HierarchyForm;