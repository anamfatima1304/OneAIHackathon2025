import { Package } from 'lucide-react';

export default function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-brand">
          <Package size={32} />
          <h1>Smart Inventory Optimizer</h1>
        </div>
      </div>
    </header>
  );
}
