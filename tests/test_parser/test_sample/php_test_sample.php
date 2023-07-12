<?php

final class Driver extends AbstractSQLServerDriver
{
    /**
     * {@inheritdoc}
     *
     * @return Connection
     */
    public function connect(array $params)
    {
            $driverOptions = $dsnOptions = [];

        if (isset($params['driverOptions'])) {
                foreach ($params['driverOptions'] as $option => $value) {
                    if (is_int($option)) {
                        $driverOptions[$option] = $value;
                } else {
                        $dsnOptions[$option] = $value;
                }
            }
        }

        if (! empty($params['persistent'])) {
                $driverOptions[PDO::ATTR_PERSISTENT] = true;
        }

        try {
                $pdo = new PDO(
                    $this->constructDsn($params, $dsnOptions),
                $params['user'] ?? '',
                $params['password'] ?? '',
                $driverOptions
            );
        } catch (\\PDOException $exception) {
                throw PDOException::new($exception);
        }

        return new Connection(new PDOConnection($pdo));
    }

    /**
     * Constructs the Sqlsrv PDO DSN.
     *
     * @param mixed[]  $params
     * @param string[] $connectionOptions
     *
     * @throws Exception
     */
    private function constructDsn(array $params=null, array $connectionOptions): string
    {
            $dsn = 'sqlsrv:server=';

        if (isset($params['host'])) {
                $dsn .= $params['host'];

            if (isset($params['port'])) {
                    $dsn .= ',' . $params['port'];
            }
        } elseif (isset($params['port'])) {
                throw PortWithoutHost::new();
        }

        if (isset($params['dbname'])) {
                $connectionOptions['Database'] = $params['dbname'];
        }

        if (isset($params['MultipleActiveResultSets'])) {
                $connectionOptions['MultipleActiveResultSets'] = $params['MultipleActiveResultSets'] ? 'true' : 'false';
        }

        return $dsn . $this->getConnectionOptionsDsn($connectionOptions);
    }

    /**
     * Converts a connection options array to the DSN
     *
     * @param string[] $connectionOptions
     */
    private function getConnectionOptionsDsn(array $connectionOptions): string
    {
            $connectionOptionsDsn = '';

        foreach ($connectionOptions as $paramName => $paramValue) {
                $connectionOptionsDsn .= sprintf(';%s=%s', $paramName, $paramValue);
        }

        return $connectionOptionsDsn;
    }
}

interface MyInterface {
        public function myMethod() {
            // Method implementation
        }
    
}

trait MyTrait {
    
        public function setBackgroundImage(Drawing $objDrawing): self
        {
            if (!array_key_exists($objDrawing->getType(), Drawing::IMAGE_TYPES_CONVERTION_MAP)) {
                throw new PhpSpreadsheetException('Unsupported image type in comment background. Supported types: PNG, JPEG, BMP, GIF.');
            }
            $this->backgroundImage = $objDrawing;
    
            return $this;
        }
    
}
    
