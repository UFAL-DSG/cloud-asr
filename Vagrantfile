# -*- mode: ruby -*- # vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "precise64-alsa"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.network "private_network", ip: "192.168.10.10"
  config.vm.synced_folder "app/", "/var/www/speech-api", type: "nfs"

  config.vm.provider :virtualbox do |vb|
    vb.memory = 2048
    vb.cpus = 1
  end

  config.vm.provision :shell, :path => "install/nginx.sh"
  config.vm.provision :shell, :path => "install/supervisord.sh"

end
