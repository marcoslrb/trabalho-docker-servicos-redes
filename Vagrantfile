Vagrant.configure("2") do |config|
  # Usar a imagem oficial do Ubuntu Server 22.04 LTS (Jammy Jellyfish)
  config.vm.box = "ubuntu/jammy64"
  
  # Aumentar o timeout de boot para compensar a lentidão do modo de compatibilidade (NEM/Hyper-V)
  config.vm.boot_timeout = 600

  # VM1 - Camada de Dados (Worker)
  config.vm.define "vm1-dados" do |dados|
    dados.vm.hostname = "vm1-dados"
    # IP estático na rede Host-Only local
    dados.vm.network "private_network", ip: "192.168.56.11"
    
    dados.vm.provider "virtualbox" do |vb|
      vb.name = "vm1-dados"
      vb.memory = "2048"
      vb.cpus = 1
      # Evitar travamento do e1000 no VirtualBox 7+ com Hyper-V ativo no Windows
      vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vb.customize ["modifyvm", :id, "--nictype2", "virtio"]
      # Ignorar falhas de MSR na coexistência do VirtualBox com Hyper-V/WSL2 e CPUs híbridas Intel
      vb.customize ["setextradata", :id, "VBoxInternal/CPUM/Msrs/IgnoreUndef", "1"]
      # Habilitar host I/O cache para evitar travamento na leitura/escrita do disco SCSI sob Hyper-V
      vb.customize ["storagectl", :id, "--name", "SCSI", "--hostiocache", "on"]
    end
  end

  # VM2 - Camada de Aplicação (Server / Control Plane)
  config.vm.define "vm2-app" do |app|
    app.vm.hostname = "vm2-app"
    # IP estático na rede Host-Only local
    app.vm.network "private_network", ip: "192.168.56.12"
    
    # Compartilha a pasta do projeto diretamente para o diretório de trabalho na VM2
    app.vm.synced_folder ".", "/home/ubuntu/trabalho", owner: "ubuntu", group: "ubuntu"

    # Redireciona as portas do NGINX NodePort para facilitar o acesso via localhost (opcional)
    app.vm.network "forwarded_port", guest: 30080, host: 30080, auto_correct: true
    app.vm.network "forwarded_port", guest: 30443, host: 30443, auto_correct: true

    app.vm.provider "virtualbox" do |vb|
      vb.name = "vm2-app"
      vb.memory = "2048"
      vb.cpus = 1
      # Evitar travamento do e1000 no VirtualBox 7+ com Hyper-V ativo no Windows
      vb.customize ["modifyvm", :id, "--nictype1", "virtio"]
      vb.customize ["modifyvm", :id, "--nictype2", "virtio"]
      # Ignorar falhas de MSR na coexistência do VirtualBox com Hyper-V/WSL2 e CPUs híbridas Intel
      vb.customize ["setextradata", :id, "VBoxInternal/CPUM/Msrs/IgnoreUndef", "1"]
      # Habilitar host I/O cache para evitar travamento na leitura/escrita do disco SCSI sob Hyper-V
      vb.customize ["storagectl", :id, "--name", "SCSI", "--hostiocache", "on"]
    end
  end
end
