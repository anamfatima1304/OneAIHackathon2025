import { TrendingUp, Package, Settings } from 'lucide-react';

interface NavigationProps {
  activeView: string;
  onViewChange: (view: string) => void;
}

export default function Navigation({ activeView, onViewChange }: NavigationProps) {
  const navItems = [
    { id: 'forecast', label: 'Forecast', icon: TrendingUp },
    { id: 'optimization', label: 'Optimization', icon: Package },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <nav className="navigation">
      {navItems.map((item) => {
        const Icon = item.icon;
        return (
          <button
            key={item.id}
            className={`nav-item ${activeView === item.id ? 'active' : ''}`}
            onClick={() => onViewChange(item.id)}
          >
            <Icon size={20} />
            <span>{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
