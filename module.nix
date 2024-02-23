{ pkgs, lib, config, ... }:

with lib;

let
  cfg = config.services.ugragatekeeper;

  configFmt = pkgs.formats.yaml {};

  configFile = configFmt.generate "ugragatekeeper.yaml" cfg.config;

  # ugragatekeeper = pkgs.callPackage "/root/ugragatekeeper" {};

in {
  options = {
    services.ugragatekeeper = {
      enable = mkEnableOption "ugragatekeeper";

      config = mkOption {
        type = configFmt.type;
        default = {};
        description = "Configuration for ugragatekeeper.";
      };

      privateConfigFile = mkOption {
        type = types.path;
        description = "Path to config file with tokens.";
      };

      domain = mkOption {
        type = types.str;
        description = "Domain to run ugragatekeeper under.";
      };
    };
  };

  config = mkIf cfg.enable {
    systemd.services."ugragatekeeper" = {
      description = "Bot for keeping order in your Telegram chat";
      wantedBy = [ "multi-user.target" ];
      after = [ "network-online.target" ];
      wants = [ "network-online.target" ];
      serviceConfig = {
        LoadCredential = "private_cfg:${cfg.privateConfigFile}";
        DynamicUser = true;
        RuntimeDirectory = "ugragatekeeper";
        RuntimeDirectoryMode = "0750";
        Group = "nginx";
        PrivateTmp = true;
      };
      path = with pkgs; [ coreutils yaml-merge ugragatekeeper ];
      script = ''
        yaml-merge ${configFile} $CREDENTIALS_DIRECTORY/private_cfg > /run/ugragatekeeper/config.yaml
        exec ugragatekeeper --config /run/ugragatekeeper/config.yaml --unix /run/ugragatekeeper/http.sock --domain ${cfg.domain}
      '';
    };

    services.nginx = {
        enable = true;

        virtualHosts."${cfg.domain}" = {
            forceSSL = true;
            enableACME = true;
            locations."/".proxyPass = "http://unix:/run/ugragatekeeper/http.sock";
        };
    };
  };
}
