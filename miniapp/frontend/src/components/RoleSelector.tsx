import React from 'react'
import './RoleSelector.css'

interface Role {
  role: string
  fio: string
}

interface RoleSelectorProps {
  roles: Role[]
  currentRole: string
  onRoleChange: (role: string) => void
}

const roleNames: Record<string, string> = {
  admin: 'Администратор',
  support: 'Поддержка',
  teacher: 'Преподаватель',
  student: 'Студент'
}

const RoleSelector: React.FC<RoleSelectorProps> = ({ roles, currentRole, onRoleChange }) => {
  if (roles.length <= 1) {
    return null
  }

  const currentRoleData = roles.find(r => r.role === currentRole)
  const currentRoleName = currentRoleData 
    ? roleNames[currentRoleData.role] || currentRoleData.role 
    : currentRole
  const currentRoleFullText = currentRoleData
    ? `${roleNames[currentRoleData.role] || currentRoleData.role} - ${currentRoleData.fio}`
    : currentRole

  return (
    <div className="role-selector">
      <div className="role-selector-label">Роль:</div>
      <div className="role-selector-wrapper" title={currentRoleFullText}>
        <select 
          value={currentRole} 
          onChange={(e) => onRoleChange(e.target.value)}
          className="role-selector-select"
        >
          {roles.map((role) => (
            <option key={role.role} value={role.role}>
              {roleNames[role.role] || role.role} - {role.fio}
            </option>
          ))}
        </select>
        <span className="role-selector-display">
          {currentRoleName}
        </span>
      </div>
    </div>
  )
}

export default RoleSelector

